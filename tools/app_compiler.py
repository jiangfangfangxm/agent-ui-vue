"""Compile app DSL files into generated runtime artifacts.

This is the first implementation of the business-configuration compiler. It is
intentionally conservative: generated artifacts are written under generated/ and
manual runtime files are never overwritten.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


class CompileError(Exception):
    """Raised when the app DSL cannot be compiled."""


@dataclass
class CompileResult:
    app_id: str
    output_dir: Path
    written_files: list[Path]
    warnings: list[str]


def _strip_comment(line: str) -> str:
    in_single = False
    in_double = False
    for index, char in enumerate(line):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return line[:index]
    return line


def _line_indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if value in {"[]", "empty_list"}:
        return []
    if value in {"{}", "empty_map"}:
        return {}
    if value in {"null", "Null", "NULL", "~"}:
        return None
    if value in {"true", "True", "TRUE"}:
        return True
    if value in {"false", "False", "FALSE"}:
        return False
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    return value


def _split_key_value(text: str) -> tuple[str, str] | None:
    if ":" not in text:
        return None
    colon_index = text.index(":")
    if colon_index + 1 < len(text) and text[colon_index + 1] != " ":
        return None
    key, value = text.split(":", 1)
    return key.strip(), value.strip()


class TinyYamlParser:
    """Small YAML subset parser for the app DSL.

    Supported syntax:
    - indentation-based mappings
    - lists of scalars
    - lists of mappings
    - scalar values: strings, numbers, booleans, null, [] and {}
    """

    def __init__(self, source: str) -> None:
        self.lines = [
            line.rstrip()
            for line in (_strip_comment(raw).rstrip() for raw in source.splitlines())
            if line.strip()
        ]

    def parse(self) -> Any:
        if not self.lines:
            return {}
        value, index = self._parse_block(0, _line_indent(self.lines[0]))
        if index != len(self.lines):
            raise CompileError(f"Unexpected YAML content at line {index + 1}.")
        return value

    def _parse_block(self, index: int, indent: int) -> tuple[Any, int]:
        if index >= len(self.lines):
            return {}, index
        stripped = self.lines[index].strip()
        if stripped.startswith("- "):
            return self._parse_list(index, indent)
        return self._parse_mapping(index, indent)

    def _parse_mapping(self, index: int, indent: int) -> tuple[dict[str, Any], int]:
        result: dict[str, Any] = {}
        while index < len(self.lines):
            line = self.lines[index]
            current_indent = _line_indent(line)
            if current_indent < indent:
                break
            if current_indent > indent:
                raise CompileError(f"Unexpected indentation at line {index + 1}: {line}")

            stripped = line.strip()
            if stripped.startswith("- "):
                break
            pair = _split_key_value(stripped)
            if not pair:
                raise CompileError(f"Expected key/value pair at line {index + 1}: {line}")
            key, raw_value = pair
            index += 1
            if raw_value:
                result[key] = _parse_scalar(raw_value)
                continue

            if index >= len(self.lines) or _line_indent(self.lines[index]) <= current_indent:
                result[key] = {}
                continue

            result[key], index = self._parse_block(index, _line_indent(self.lines[index]))
        return result, index

    def _parse_list(self, index: int, indent: int) -> tuple[list[Any], int]:
        result: list[Any] = []
        while index < len(self.lines):
            line = self.lines[index]
            current_indent = _line_indent(line)
            if current_indent < indent:
                break
            if current_indent > indent:
                raise CompileError(f"Unexpected indentation at line {index + 1}: {line}")

            stripped = line.strip()
            if not stripped.startswith("- "):
                break

            item_text = stripped[2:].strip()
            index += 1
            pair = _split_key_value(item_text)
            if pair:
                key, raw_value = pair
                item: dict[str, Any] = {}
                if raw_value:
                    item[key] = _parse_scalar(raw_value)
                elif index < len(self.lines) and _line_indent(self.lines[index]) > current_indent:
                    item[key], index = self._parse_block(index, _line_indent(self.lines[index]))
                else:
                    item[key] = {}

                if index < len(self.lines) and _line_indent(self.lines[index]) > current_indent:
                    extra, index = self._parse_block(index, _line_indent(self.lines[index]))
                    if not isinstance(extra, dict):
                        raise CompileError(
                            f"Expected mapping continuation for list item at line {index + 1}."
                        )
                    item.update(extra)
                result.append(item)
                continue

            if item_text:
                result.append(_parse_scalar(item_text))
                continue

            if index >= len(self.lines) or _line_indent(self.lines[index]) <= current_indent:
                result.append(None)
                continue

            item_value, index = self._parse_block(index, _line_indent(self.lines[index]))
            result.append(item_value)
        return result, index


def load_app_config(path: Path) -> dict[str, Any]:
    data = TinyYamlParser(path.read_text(encoding="utf-8")).parse()
    if not isinstance(data, dict):
        raise CompileError("App config root must be a mapping.")
    return data


def _require_mapping(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise CompileError(f"Missing or invalid mapping: {key}")
    return value


def _as_list(value: Any, *, name: str) -> list[Any]:
    if not isinstance(value, list):
        raise CompileError(f"Expected list: {name}")
    return value


def _event_name_from_contract(value: str) -> str:
    return value.split(":", 1)[0]


def validate_config(config: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    app = _require_mapping(config, "app")
    states = _require_mapping(config, "states")
    events = _require_mapping(config, "events")
    sections = _require_mapping(config, "sections")
    context = _require_mapping(config, "context")

    app_id = app.get("id")
    if not isinstance(app_id, str) or not app_id:
        raise CompileError("app.id must be a non-empty string.")

    entry_state = app.get("entryState")
    if entry_state not in states:
        raise CompileError(f"app.entryState references unknown state: {entry_state}")

    initial_event = app.get("initialEvent")
    if initial_event not in events:
        raise CompileError(f"app.initialEvent references unknown event: {initial_event}")

    for state_id, state in states.items():
        if not isinstance(state, dict):
            raise CompileError(f"State must be a mapping: {state_id}")
        for event_id in _as_list(state.get("allowedEvents", []), name=f"{state_id}.allowedEvents"):
            if event_id not in events:
                raise CompileError(f"State {state_id} references unknown event: {event_id}")
        for section_id in _as_list(
            state.get("visibleSections", []), name=f"{state_id}.visibleSections"
        ):
            if section_id not in sections:
                raise CompileError(f"State {state_id} references unknown section: {section_id}")

    for mode_id, mode in (config.get("modes") or {}).items():
        if not isinstance(mode, dict):
            raise CompileError(f"Mode must be a mapping: {mode_id}")
        base_state = mode.get("baseState")
        if base_state not in states:
            raise CompileError(f"Mode {mode_id} references unknown baseState: {base_state}")
        for event_id in _as_list(mode.get("allowedEvents", []), name=f"{mode_id}.allowedEvents"):
            if event_id not in events:
                raise CompileError(f"Mode {mode_id} references unknown event: {event_id}")

    for event_id, event in events.items():
        if not isinstance(event, dict):
            raise CompileError(f"Event must be a mapping: {event_id}")
        for state_id in _as_list(event.get("allowedStates", []), name=f"{event_id}.allowedStates"):
            if state_id not in states and state_id not in {
                "presenting_result",
            }:
                raise CompileError(f"Event {event_id} references unknown state: {state_id}")
        for mode_id in event.get("allowedModes", []) or []:
            if mode_id not in (config.get("modes") or {}):
                raise CompileError(f"Event {event_id} references unknown mode: {mode_id}")

        transition = event.get("transition") or {}
        if isinstance(transition, dict):
            for field in transition.get("contextWrites", []) or []:
                if field not in context:
                    raise CompileError(f"Event {event_id} writes unknown context field: {field}")
            _validate_section_effects(event_id, transition.get("sectionEffects") or {}, sections)
            for branch in transition.get("conditional", []) or []:
                if not isinstance(branch, dict):
                    raise CompileError(f"Event {event_id} conditional branch must be a mapping.")
                to_state = branch.get("toState")
                if to_state not in states and to_state != "same":
                    raise CompileError(
                        f"Event {event_id} conditional branch references unknown state: {to_state}"
                    )
                for field in branch.get("contextWrites", []) or []:
                    if field not in context:
                        raise CompileError(
                            f"Event {event_id} conditional branch writes unknown context field: {field}"
                        )
                _validate_section_effects(event_id, branch.get("sectionEffects") or {}, sections)

    for section_id, section in sections.items():
        if not isinstance(section, dict):
            raise CompileError(f"Section must be a mapping: {section_id}")
        for binding in section.get("contextBindings", []) or []:
            if binding not in context:
                raise CompileError(f"Section {section_id} binds unknown context field: {binding}")
        binding = section.get("contextBinding")
        if binding and binding not in context:
            raise CompileError(f"Section {section_id} binds unknown context field: {binding}")

    test_contracts = config.get("testContracts") or {}
    for path in test_contracts.get("requiredPaths", []) or []:
        for event_ref in path.get("events", []) or []:
            event_id = _event_name_from_contract(str(event_ref))
            if event_id not in events:
                raise CompileError(
                    f"Test contract {path.get('name')} references unknown event: {event_id}"
                )

    if not (config.get("compiler") or {}).get("generationPolicy", {}).get(
        "requireContractTests", False
    ):
        warnings.append("compiler.generationPolicy.requireContractTests is not enabled.")

    return warnings


def _validate_section_effects(
    event_id: str,
    effects: dict[str, Any],
    sections: dict[str, Any],
) -> None:
    for key in ("replace", "remove"):
        for section_id in effects.get(key, []) or []:
            if section_id not in sections:
                raise CompileError(f"Event {event_id} {key} references unknown section: {section_id}")
    for before_id, appended in (effects.get("appendBefore") or {}).items():
        if before_id not in sections:
            raise CompileError(f"Event {event_id} appendBefore references unknown anchor: {before_id}")
        for section_id in appended or []:
            if section_id not in sections:
                raise CompileError(
                    f"Event {event_id} appendBefore references unknown section: {section_id}"
                )


def write_text(path: Path, content: str, written_files: list[Path]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    written_files.append(path)


def compile_app(config_path: Path, output_root: Path) -> CompileResult:
    config = load_app_config(config_path)
    warnings = validate_config(config)
    app_id = config["app"]["id"]
    output_dir = output_root / app_id
    written_files: list[Path] = []

    write_text(
        output_dir / "app.normalized.json",
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        written_files,
    )
    write_text(
        output_dir / "frontend" / "workflow-definition.generated.ts",
        render_frontend_workflow_definition(config),
        written_files,
    )
    write_text(
        output_dir / "python" / "workflow_definition.generated.py",
        render_python_workflow_definition(config),
        written_files,
    )
    write_text(
        output_dir / "tests" / "test_transition_contracts.generated.py",
        render_transition_contract_tests(config),
        written_files,
    )
    write_text(
        output_dir / "README.generated.md",
        render_compile_readme(config, written_files),
        written_files,
    )

    return CompileResult(
        app_id=app_id,
        output_dir=output_dir,
        written_files=written_files,
        warnings=warnings,
    )


def render_frontend_workflow_definition(config: dict[str, Any]) -> str:
    events = config["events"]
    states = config["states"]
    lines = [
        "/* AUTO-GENERATED from app DSL. Do not edit by hand. */",
        'import type { WorkflowEventInput, WorkflowState } from "../../src/types/workflow";',
        "",
        "export type GeneratedWorkflowEventType =",
    ]
    for event_id in events:
        lines.append(f'  | "{event_id}"')
    lines[-1] += ";"
    lines.extend(
        [
            "",
            "type PayloadValidator = (payload: Record<string, unknown>) => boolean;",
            "",
            "interface GeneratedEventContract {",
            "  eventType: GeneratedWorkflowEventType;",
            "  allowedStates: WorkflowState[];",
            "  validatePayload: PayloadValidator;",
            "}",
            "",
            "function hasNonEmptyString(payload: Record<string, unknown>, key: string): boolean {",
            '  return typeof payload[key] === "string" && payload[key].trim().length > 0;',
            "}",
            "",
            "const optionalPayload: PayloadValidator = () => true;",
            "",
            "export const generatedEventContracts: Record<GeneratedWorkflowEventType, GeneratedEventContract> = {",
        ]
    )
    for event_id, event in events.items():
        validator = render_ts_validator(event.get("payloadSchema") or {})
        allowed_states = json.dumps(event.get("allowedStates", []), ensure_ascii=False)
        lines.extend(
            [
                f"  {json.dumps(event_id)}: {{",
                f"    eventType: {json.dumps(event_id)},",
                f"    allowedStates: {allowed_states} as WorkflowState[],",
                f"    validatePayload: {validator},",
                "  },",
            ]
        )
    lines.extend(
        [
            "};",
            "",
            "export const generatedAllowedEventsByState: Record<string, GeneratedWorkflowEventType[]> = {",
        ]
    )
    for state_id, state in states.items():
        events_json = json.dumps(state.get("allowedEvents", []), ensure_ascii=False)
        lines.append(f"  {json.dumps(state_id)}: {events_json} as GeneratedWorkflowEventType[],")
    lines.extend(
        [
            "};",
            "",
            "export function validateGeneratedEventInput(",
            "  state: WorkflowState,",
            "  input: WorkflowEventInput,",
            "): string | null {",
            "  const contract = generatedEventContracts[input.type as GeneratedWorkflowEventType];",
            "  if (!contract) return `未知事件：${input.type}`;",
            "  if (!contract.allowedStates.includes(state)) return `事件“${input.type}”不属于当前阶段“${state}”`;",
            "  if (!contract.validatePayload(input.payload ?? {})) return `事件“${input.type}”的 payload 不符合契约`;",
            "  return null;",
            "}",
            "",
        ]
    )
    return "\n".join(lines)


def render_ts_validator(payload_schema: dict[str, Any]) -> str:
    required = payload_schema.get("required") or []
    properties = payload_schema.get("properties") or {}
    checks: list[str] = []
    for field in required:
        prop = properties.get(field) or {}
        if prop.get("minLength", 0) >= 1 or prop.get("type") == "string":
            checks.append(f'hasNonEmptyString(payload, "{field}")')
        else:
            checks.append(f'payload["{field}"] !== undefined')
    for field, prop in properties.items():
        enum_values = prop.get("enum")
        if enum_values:
            values = json.dumps(enum_values, ensure_ascii=False)
            checks.append(f"({values} as unknown[]).includes(payload[{json.dumps(field)}])")
    if not checks:
        return "optionalPayload"
    return f"(payload) => {' && '.join(checks)}"


def render_python_workflow_definition(config: dict[str, Any]) -> str:
    events = config["events"]
    states = config["states"]
    lines = [
        '"""AUTO-GENERATED from app DSL. Do not edit by hand."""',
        "",
        "from __future__ import annotations",
        "",
        "from typing import Any, Dict, List",
        "",
        "",
        "def _optional_payload(_: Dict[str, Any]) -> bool:",
        "    return True",
        "",
        "",
        "def _has_non_empty_string(payload: Dict[str, Any], key: str) -> bool:",
        "    value = payload.get(key)",
        "    return isinstance(value, str) and bool(value.strip())",
        "",
        "",
        "EVENT_CONTRACTS: Dict[str, Dict[str, Any]] = {",
    ]
    for event_id, event in events.items():
        validator = render_python_validator(event.get("payloadSchema") or {})
        lines.extend(
            [
                f"    {event_id!r}: {{",
                f"        'states': {event.get('allowedStates', [])!r},",
                f"        'validate_payload': {validator},",
                "    },",
            ]
        )
    lines.extend(["}", "", "", "ALLOWED_EVENTS_BY_STATE: Dict[str, List[str]] = {"])
    for state_id, state in states.items():
        lines.append(f"    {state_id!r}: {state.get('allowedEvents', [])!r},")
    lines.extend(
        [
            "}",
            "",
            "",
            "def allowed_events_for_state(state: str) -> List[str]:",
            "    return list(dict.fromkeys(ALLOWED_EVENTS_BY_STATE.get(state, ['open_detail'])))",
            "",
            "",
            "def validate_event_contract(state: str, event: Dict[str, Any]) -> None:",
            "    event_type = str(event.get('type', ''))",
            "    contract = EVENT_CONTRACTS.get(event_type)",
            "    if not contract:",
            "        raise ValueError(f'Unsupported event type: {event_type}')",
            "    if state not in contract['states']:",
            "        raise ValueError(f\"Event '{event_type}' is not allowed in state '{state}'\")",
            "    if not contract['validate_payload'](event.get('payload') or {}):",
            "        raise ValueError(f\"Event '{event_type}' payload does not match its contract\")",
            "",
        ]
    )
    return "\n".join(lines)


def render_python_validator(payload_schema: dict[str, Any]) -> str:
    required = payload_schema.get("required") or []
    properties = payload_schema.get("properties") or {}
    checks: list[str] = []
    for field in required:
        prop = properties.get(field) or {}
        if prop.get("minLength", 0) >= 1 or prop.get("type") == "string":
            checks.append(f"_has_non_empty_string(payload, {field!r})")
        else:
            checks.append(f"{field!r} in payload")
    for field, prop in properties.items():
        enum_values = prop.get("enum")
        if enum_values:
            checks.append(f"payload.get({field!r}) in {set(enum_values)!r}")
    if not checks:
        return "_optional_payload"
    return "lambda payload: " + " and ".join(checks)


def render_transition_contract_tests(config: dict[str, Any]) -> str:
    app_id = config["app"]["id"]
    paths = (config.get("testContracts") or {}).get("requiredPaths", []) or []
    lines = [
        '"""AUTO-GENERATED transition contract skeleton from app DSL."""',
        "",
        "# This file is generated as a contract artifact. It intentionally does not",
        "# import the live runtime yet; the next compiler phase will bind these",
        "# contracts to generated handlers or the project patch service.",
        "",
        f"APP_ID = {app_id!r}",
        "",
        "REQUIRED_PATHS = [",
    ]
    for path in paths:
        lines.append(f"    {path!r},")
    lines.extend(
        [
            "]",
            "",
            "",
            "def test_generated_contracts_are_present():",
            "    assert REQUIRED_PATHS",
            "    for path in REQUIRED_PATHS:",
            "        assert path.get('name')",
            "        assert path.get('events')",
            "        assert path.get('expectedState')",
            "",
        ]
    )
    return "\n".join(lines)


def render_compile_readme(config: dict[str, Any], written_files: Iterable[Path]) -> str:
    app = config["app"]
    lines = [
        f"# Generated Artifacts: {app['name']}",
        "",
        "This directory was generated from the app DSL.",
        "",
        "## Source",
        "",
        f"- App id: `{app['id']}`",
        f"- Runtime: `{app.get('runtime', '')}`",
        f"- Entry state: `{app.get('entryState', '')}`",
        f"- Initial event: `{app.get('initialEvent', '')}`",
        "",
        "## Files",
        "",
    ]
    for file_path in written_files:
        lines.append(f"- `{file_path.name}`")
    lines.extend(
        [
            "",
            "Generated artifacts are not wired into the runtime automatically yet.",
            "Use them as the stable output contract for the next compiler phase.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile an app DSL file.")
    parser.add_argument("config", type=Path, help="Path to *.app.yaml")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("generated"),
        help="Output root directory. Defaults to generated/",
    )
    args = parser.parse_args()

    try:
        result = compile_app(args.config, args.out)
    except CompileError as error:
        print(f"[app-compiler] ERROR: {error}")
        return 1

    print(f"[app-compiler] compiled app: {result.app_id}")
    print(f"[app-compiler] output: {result.output_dir}")
    for warning in result.warnings:
        print(f"[app-compiler] warning: {warning}")
    for file_path in result.written_files:
        print(f"[app-compiler] wrote: {file_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
