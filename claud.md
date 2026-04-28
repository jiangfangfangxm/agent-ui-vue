# CLAUDE.md

## Project Goal

This project is an agent-driven runtime UI built with Vue 3 and Element Plus.

The goal is to support Human-in-the-Loop workflows where an AI agent decides the next step, the frontend renders UI from schema, and user actions are sent back as structured events.

## Core Concepts

- Schema-driven UI: pages and widgets are rendered from JSON schema.
- Runtime state: frontend keeps a workflow envelope as the source of truth.
- Patch updates: the agent or backend sends patches to update parts of the UI.
- Human-in-the-loop: user actions are captured as structured workflow events.

## Tech Stack

- Vue 3
- TypeScript
- Element Plus
- Vite
- JSON schema / custom UI schema
- Patch-based runtime updates

## Important Files

- `src/types/workflow.ts`: core workflow types.
- `src/runtime/useWorkflowRuntime.ts`: runtime state and dispatch logic.
- `src/widgets/ChecklistWidget.vue`: checklist widget renderer.
- `src/widgets/widgetContract.ts`: widget type contracts.
- `src/App.vue`: demo entry point.

## Development Commands

```bash
npm install
npm run dev
npm run build
npm run preview