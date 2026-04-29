"""Local HTTP patch service for frontend integration tests."""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List

from agent_patch_builders.workflow_action_builders import (
    build_add_checklist_item_patches,
    build_init_event_patches,
    build_open_detail_patches,
    build_risk_check_event_patches,
    build_toggle_checklist_item_patches,
)


def build_patch_plan(payload: Dict[str, Any]) -> Dict[str, Any]:
    envelope = payload["envelope"]
    event = payload["event"]
    event_type = str(event["type"])

    if event_type == "init_event":
        patches = build_init_event_patches(envelope=envelope, event=event)
    elif event_type == "toggle_check":
        patches = build_toggle_checklist_item_patches(
            envelope=envelope,
            event=event,
        )
    elif event_type == "add_checklist_item":
        patches = build_add_checklist_item_patches(
            envelope=envelope,
            event=event,
        )
    elif event_type == "Risk_Check_Event":
        patches = build_risk_check_event_patches(
            envelope=envelope,
            event=event,
        )
    elif event_type == "open_detail":
        patches = build_open_detail_patches(event=event)
    else:
        raise ValueError(f"Unsupported event type: {event_type}")

    return {
      "patches": patches,
      "rationale": f"Python patch service generated {len(patches)} patch operations for event '{event_type}'.",
      "warnings": [],
    }


class PatchServiceHandler(BaseHTTPRequestHandler):
    server_version = "LocalPatchService/0.1"

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(HTTPStatus.NO_CONTENT)
        self._write_default_headers()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._write_json(
                HTTPStatus.OK,
                {
                    "status": "ok",
                    "service": "python-patch-service",
                },
            )
            return

        self._write_json(
            HTTPStatus.NOT_FOUND,
            {"error": "Not found"},
        )

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/patch-plan":
            self._write_json(
                HTTPStatus.NOT_FOUND,
                {"error": "Not found"},
            )
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length)
            payload = json.loads(raw_body.decode("utf-8"))
            result = build_patch_plan(payload)
        except KeyError as error:
            self._write_json(
                HTTPStatus.BAD_REQUEST,
                {"error": f"Missing required field: {error}"},
            )
            return
        except ValueError as error:
            self._write_json(
                HTTPStatus.BAD_REQUEST,
                {"error": str(error)},
            )
            return
        except json.JSONDecodeError:
            self._write_json(
                HTTPStatus.BAD_REQUEST,
                {"error": "Invalid JSON body"},
            )
            return
        except Exception as error:  # noqa: BLE001
            self._write_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": f"Patch service failed: {error}"},
            )
            return

        self._write_json(HTTPStatus.OK, result)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[patch-service] {self.address_string()} - {format % args}")

    def _write_default_headers(self) -> None:
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _write_json(self, status: HTTPStatus, payload: Dict[str, Any]) -> None:
        response = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._write_default_headers()
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), PatchServiceHandler)
    print(f"Python patch service listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
