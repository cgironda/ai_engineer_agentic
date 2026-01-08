# Development Task Plan: AI-Driven Trading App (Gradio + Svelte)

Our main goal for the AI-Driven Trading App is to help traders get quick insights into market trends and make decisions faster. To support this, we are building a strong UI layer. **Gradio** will let us quickly design and test features, while Svelte will make the interface more dynamic and responsive. The backend logic will be handled by the multi-agent program in `crew_prj/dev_team/output_cp/app.py`, following the account rules in `crew_prj/dev_team/output_cp/accounts.py_design.md`.

## Goals
- Preserve the existing Gradio experience as the production UI layer for rapid iteration and QA.
- Add a Svelte front end that consumes a stable JSON API from the Python service.
- Align account behavior and validations with the design specification.
- Keep implementation safe, testable, and deployment-ready.

## Inputs and Constraints
- Entrypoint: `crew_prj/dev_team/output_cp/app.py` (Gradio UI; currently uses a global account singleton).
- Design spec: `crew_prj/dev_team/output_cp/accounts.py_design.md` (Account class rules and share pricing).
- Do not write code in this phase; create a task list and plan for Codex to implement. Prioritize constraints using a 'must/should/could' hierarchy to help Codex negotiate trade-offs when conflicts arise. For example, session security must be ensured, removal of the global singleton should be prioritized, and additional optimizations could be considered as time allows.

## Target Architecture
Understanding the core architectural drivers, such as performance, scalability, and testability, is essential for guiding the design decisions of our AI-driven trading app. These drivers ensure that our system can efficiently handle increasing workloads, remain robust across various operational conditions, and support thorough testing. With these priorities in mind, our targeted architecture is detailed below.

1. **Backend service**: Gradio Blocks UI remains available for QA and manual testing.
2. **API layer**: Add a JSON API (FastAPI mounted alongside Gradio) for Svelte consumption.
3. **Svelte app**: SvelteKit SPA that calls the JSON endpoints for all account/trade flows.
4. **State**: Switch from a global account to a session-based account registry. Using a global singleton has caused problems like user session conflicts and limited scalability. A session-based registry keeps each user’s data separate, improving security and performance. This also helps manage resources better and follows best practices.
5. **Safety**: Centralized validation and consistent errors for Gradio and API clients.

## Task List (for Codex implementation)
1. **Account Domain Alignment**
   - Compare `crew_prj/dev_team/output_cp/accounts.py` with `crew_prj/dev_team/output_cp/accounts.py_design.md`.
   - Ensure `Account` includes `initial_deposit` and uses it for `calculate_profit_loss`.
   - Confirm validations: positive deposit/withdraw/quantity, no overdrafts, no overselling, reject unknown symbols.
   - Ensure `get_share_price` returns `0.0` for unknown symbols and centralize the supported symbols list.

2. **Backend State Management**
   - Replace the global `account` singleton with a session registry keyed by token.
   - Add helper utilities to create/get accounts per session.
   - Standardize error responses so **Gradio** and the API can share the same logic.

3. **JSON API Contract**
   - Define explicit endpoints: `create_account`, `deposit`, `withdraw`, `buy`, `sell`, `status`, `holdings`, `transactions`, `prices`.
   - Use a common response schema: `{success, message, data?, error?}`.
   - Return structured data objects for balances, holdings, and profit/loss.
   - Configure CORS for the Svelte dev server.

4. **Gradio UI Hardening**
   - Keep the Gradio interface in `crew_prj/dev_team/output_cp/app.py`.
   - Wire Gradio buttons to the same handlers used by the JSON API.
   - Improve error messaging for missing accounts and invalid inputs.

5. **Svelte App Scaffolding**
   - Create a SvelteKit app at `crew_prj/dev_team/ui/` with TypeScript enabled.
   - Add routes: `Dashboard`, `Trade`, `Transactions`, `Settings`.
   - Build a typed API client module (base URL, token header, error handling).
   - Implement components: account creation, deposit/withdraw, buy/sell, holdings summary.
   - Add lightweight charting for portfolio value history.

6. **Session and Auth Flow**
   - Establish a minimal token-based session (frontend stores token; backend maps token to account).
   - Include token in headers for all API requests.
   - Add guardrails to prevent cross-session access.

7. **Testing and Quality Gates**
   - Unit tests for account behaviors (deposit, withdraw, buy/sell, P/L, portfolio value).
   - API contract tests for each endpoint with valid and invalid inputs.
   - UI integration tests for core flows (create account, trade, view holdings).
   - Add linting and formatting for Python and Svelte.

8. **Deployment and Ops**
   - Add `.env.example` for API base URL, CORS, and session settings.
   - Provide unified scripts: `dev:backend`, `dev:frontend`, `test`, `lint`.
   - Document containerization strategy with health checks.

9. **Documentation**
   - Update `crew_prj/dev_team/README.md` with architecture, setup, and API examples.
   - Document how Gradio and Svelte coexist and how to run each in dev.

## Suggested Implementation Plan
1. **Domain alignment**: reconcile the `Account` implementation to match the design spec.
2. **State model**: introduce a session registry and shared helpers.
3. **API layer**: mount FastAPI routes with a consistent response schema and CORS.
4. **Gradio wiring**: update UI callbacks to use the shared backend logic.
5. **Svelte scaffold**: add the SvelteKit app, API client, and core pages.
6. **Feature flows**: build account, trading, and reporting UI flows.
7. **Testing & QA**: add unit, API, and UI tests.
8. **Docs & ops**: finalize README updates and deployment guidance.

