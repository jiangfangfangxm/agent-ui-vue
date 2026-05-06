# CLAUDE.md

## Project

`agent-ui-vue` is an **Agent-driven UI Runtime Engine** demo built with Vue 3, Element Plus, TypeScript, and a local Python patch service.

The current product scenario is the **Warning Review Workbench**:

```text
risk review -> risk identification -> follow-up action plan
```

This is not a conventional component-owned-state frontend. The runtime flow is:

```text
page init / user action
-> WorkflowEvent
-> useWorkflowRuntime()
-> Patch Planner
-> PatchOperation[]
-> applyPatches()
-> WorkflowEnvelope
-> Renderer
-> UI update
```

## Core Rules

- `WorkflowEnvelope` is the runtime source of truth for UI state.
- `WorkflowContext` stores real business state.
- Widgets emit `WorkflowEvent`; they must not mutate the envelope directly.
- All UI/business updates should be represented as `PatchOperation[]`.
- `allowedEvents` controls which interactions are valid in the current workflow state.
- Event contracts are validated on both the frontend and Python service side.

## Current Workflow States

- `reviewing`: risk review
- `report_reviewing`: report handling
- `awaiting_revision`: report edit subflow
- `risk_identifying`: risk identification
- `action_planning`: follow-up action plan
- `resolved_no_risk`: completed without risk
- `resolved_with_action`: completed with action plan
- `presenting_result`: compatibility/result display state

## Important Events

- Init: `init_event`
- Review: `toggle_check`, `add_checklist_item`, `Risk_Check_Event`, `open_detail`
- Report: `edit_report`, `save_report_revision`, `cancel_report_revision`, `add_review_direction_after_report`, `submit_new_direction_after_report`, `cancel_add_direction`, `enter_risk_identification`
- Risk identification: `set_risk_decision`, `update_risk_reason`, `resolve_no_risk`, `confirm_risk_identification`
- Action plan: `toggle_action_item`, `add_action_item`, `confirm_action_plan`

## Important Files

Frontend:

- `src/App.vue`: app entry, auto-dispatches `init_event`, switches between runtime and config tool.
- `src/composables/useWorkflowRuntime.ts`: runtime state, event dispatch, planner call, patch application, error handling.
- `src/types/workflow.ts`: core protocol types.
- `src/workflow/definition.ts`: frontend event contract entry, prefers generated config.
- `src/workflow/appConfig.ts`: loads `generated/warning_review_workbench/app.normalized.json`.
- `src/utils/patch.ts`: frontend patch engine and the only frontend state mutation gateway.
- `src/agent/HttpPatchPlannerModel.ts`: calls the Python patch service through `/api/patch-plan`.
- `src/components/renderer/`: schema renderer.
- `src/components/widgets/`: widget implementations.
- `src/components/config/BusinessConfigTool.vue`: first version of the business configuration tool.
- `src/mock/initialEnvelope.ts`: minimal boot envelope; do not put real business data here.

Python:

- `python/patch_service.py`: local HTTP patch service on `127.0.0.1:8000`.
- `python/agent_patch_builders/app_config_loader.py`: generated config loader.
- `python/agent_patch_builders/workflow_definition.py`: Python event contracts and allowed-events inference.
- `python/agent_patch_builders/workflow_action_builders.py`: business event patch builders.
- `python/agent_patch_builders/section_builders.py`: UI section builders.
- `python/tests/`: unit and contract tests.

Business DSL and compiler:

- `apps/warning-review.app.yaml`: current business DSL source.
- `tools/app_compiler.py`: CLI compiler/assembler.
- `generated/warning_review_workbench/app.normalized.json`: normalized config loaded by frontend and Python.
- `generated/warning_review_workbench/frontend/workflow-definition.generated.ts`: generated frontend contract reference.
- `generated/warning_review_workbench/python/workflow_definition.generated.py`: generated Python contract reference.
- `generated/warning_review_workbench/tests/test_transition_contracts.generated.py`: generated transition-contract test skeleton.

## Business Configuration Tool

The frontend has a first version of a business configuration tool. Use the top-right switch:

```text
运行台 / 配置工具
```

It currently supports:

- editing app metadata
- viewing context fields
- editing states, `allowedEvents`, and `visibleSections`
- editing events, handlers, allowed states, and target state
- viewing section/widget bindings
- validating references
- exporting the in-memory config as YAML
- showing a compile page with checks, CLI command, and expected artifacts

Current limits:

- It does not write back to `apps/warning-review.app.yaml`.
- It does not execute local Python from the browser.
- After export, manually save the DSL and run the compiler.

## Commands

Install dependencies:

```bash
npm install
```

Start Python patch service:

```bash
cd python
python patch_service.py
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Start frontend:

```bash
npm run dev
```

Run Python tests:

```bash
python -m unittest discover -s python/tests -p "test_*.py"
```

Run TypeScript check:

```bash
.\node_modules\.bin\vue-tsc.cmd --noEmit
```

Compile the business DSL:

```bash
python tools\app_compiler.py apps\warning-review.app.yaml
```

If the frontend reports `connect ECONNREFUSED 127.0.0.1:8000`, the Python patch service is not running or is unreachable.

## Maintenance Guidance

- Prefer adding a new `WorkflowEvent` over adding direct widget state mutations.
- Model new workflow steps with `state + visibleSections + allowedEvents`.
- Keep real business data in `WorkflowContext`.
- Use patches for all runtime updates.
- Do not move real business data back into `initialEnvelope.ts`.
- Keep generated config as the contract source, but do not let compiler output overwrite hand-maintained runtime code.
- Keep Python patch builders split by business action.
- Be careful when touching renderer key strategy, report-stage actions, or `allowedEvents`; these areas need focused regression.

## Regression Checklist

After workflow changes, verify:

1. page load dispatches `init_event`
2. warning details are populated
3. review directions render correctly
4. adding review directions in review stage writes back
5. executing review creates report and report actions
6. report edit subflow opens, saves, and cancels correctly
7. adding review direction after report refreshes the report and returns to report stage
8. no-risk path resolves the task
9. has-risk path enters action planning
10. action items can be toggled, added, and confirmed
11. config tool opens, validates, exports YAML, and displays compile guidance

## Current Risks

- The debug panel is useful but temporary.
- The config tool is in-memory only; save and one-click compile are future work.
- Generated files are stable contract artifacts, while complex patch builders remain handwritten.
- Section/component re-rendering relies on current key strategy.
- Report-stage buttons and subflows are sensitive to `allowedEvents`.
