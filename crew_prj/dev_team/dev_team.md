# Development Task Plan: AI-Driven Trading App (Gradio + Svelte)

This document outlines tasks for building a production-grade UI layer with **Gradio** (Python rapid-prototyping) enhanced by a **Svelte** front-end, targeting the multi-agent program in `crew_prj/dev_team/output_4o/app.py` and the account domain design in `crew_prj/dev_team/output_4o/accounts.py_design.md`.

## Goals
- Deliver a user-facing trading simulation experience powered by the existing multi-agent logic.
- Keep Gradio as the Python-first interaction layer while layering Svelte for richer, production-ready UX.
- Ensure the app is safe, testable, and ready for incremental deployment.

## Current Inputs
- Python entrypoint: `crew_prj/dev_team/output_4o/app.py`
- Account logic & design notes: `crew_prj/dev_team/output_4o/accounts.py` and `.../accounts.py_design.md`

## High-Level Architecture Direction
1. **Backend (Gradio service)**: Expose typed, side-effect-aware endpoints for account lifecycle, portfolio actions, and reporting. Avoid `eval`-style routing; use explicit handlers.
2. **API Surface**: Prefer clean function signatures returned by Gradio’s `FastAPI` mount or a thin FastAPI wrapper for Svelte to consume via HTTP/JSON.
3. **Front-End (Svelte)**: Svelte SPA that consumes the backend endpoints, offers dashboards (balances, holdings, P/L), and wraps interactive flows (create account, buy/sell, deposits/withdrawals).
4. **State & Persistence**: Start in-memory; add persistence interfaces to allow future DB support without blocking UI work.
5. **Observability & Safety**: Logging, validation, and error surfaces both in Gradio (developer surface) and Svelte (user surface).

## Task List (for Codex implementation)
1. **Stabilize Core Backend Interfaces**
   - Refactor `app.py` to replace the `eval`-driven action router with explicit functions and a safe dispatcher.
   - Ensure `Account` methods enforce type/amount validation and return structured results (status, message, data).
   - Add dependency-injected price getter and clock utilities for testability.

2. **Expose Programmatic API for Svelte**
   - Promote the Gradio interface to also expose a `FastAPI`/`/api` router (supported by Gradio) with JSON endpoints for: create account, deposit, withdraw, buy, sell, holdings, transactions, portfolio value, profit/loss.
   - Standardize response schema: `{success: bool, message: str, data?: object, error?: string}`.
   - Add CORS configuration for the Svelte dev server.

3. **Design Gradio Developer Console**
   - Keep a Gradio UI for rapid experimentation (forms per operation, live logs, preview of portfolio data).
   - Include validation messages and disable actions when the account context is missing.
   - Add simple session management (per user) to avoid global state collisions.

4. **Build Svelte Production UI**
   - Scaffold a Svelte SPA (e.g., `crew_prj/dev_team/ui/`) with routes for Dashboard, Trades, Transactions, and Settings.
   - Implement API client module pointing to the backend JSON routes.
   - Add components for account creation, deposit/withdraw, buy/sell flows with optimistic UI and error toasts.
   - Create data visualizations (balances over time, holdings composition) using a lightweight chart lib.

5. **Authentication & Session Handling**
   - Add minimal auth/session tokens (even if mocked) to tag accounts per user.
   - Pass session identifiers from Svelte to backend endpoints; prevent cross-session data leaks.

6. **Testing & Quality**
   - Unit tests for `Account` behaviors (deposits, withdrawals, buy/sell validation, P/L).
   - API contract tests for each JSON endpoint.
   - Svelte integration tests for critical flows (create account, buy/sell).
   - Linting/formatting for Python (ruff/black) and Svelte/TypeScript (eslint/prettier).

7. **Deployment & Ops**
   - Provide `.env.example` for API base URL and CORS origins.
   - Add a unified `Makefile`/`npm` scripts: `dev:backend` (Gradio/FastAPI), `dev:frontend` (Svelte), `test`, `lint`.
   - Containerize both layers with a multi-stage build; ensure health checks for API readiness.

8. **Documentation**
   - Update README with architecture diagram, start commands, and API examples.
   - Add developer notes on how Svelte consumes the Gradio/FastAPI endpoints and how to run end-to-end locally.

## Suggested Implementation Plan (stepwise)
1. **Backend refactor**: Clean routing, structured responses, validation; wire price getter injection.
2. **API exposure**: Mount FastAPI routes alongside Gradio UI; add CORS; document endpoints.
3. **Session model**: Introduce per-user account storage keyed by session token.
4. **Front-end scaffold**: Create Svelte project, API client, and shared UI components.
5. **Feature flows**: Build pages for account lifecycle and trading operations with live portfolio widgets.
6. **Quality gates**: Add tests/linting scripts; integrate into CI (GitHub Actions if available).
7. **Docs & ops**: Finalize README, env samples, and containerization.

Use this checklist to guide Codex in writing and executing the required code without deviating from the architecture above.
