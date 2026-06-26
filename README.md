# Finance Agent Service

This repo started as a mock tool-calling interview exercise and now includes a
production-style foundation for an audit-ready finance agent backend.

The first production use case is transaction review: given a transaction ID, the
service gathers synthetic ledger, contract, policy, audit evidence, and
historical-decision context, then returns a structured review decision.

## Stack

- FastAPI for the HTTP backend
- Pydantic for API, domain, and tool schema validation
- OpenAI Agents SDK for the live model-backed agent path
- Synthetic JSON finance data for deterministic local development
- Docker for local service startup

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"
copy .env.example .env
```

Set `OPENAI_API_KEY` in `.env` before enabling live OpenAI calls. The current
foundation can run deterministic transaction reviews without an API key.

Use deterministic mode for local tests:

```text
AGENT_MODE=deterministic
```

Use live OpenAI mode:

```text
AGENT_MODE=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-mini
```

## Run Tests

```bash
python -m unittest -v
python -m pytest -q
```

## Run Evals

Evals exercise agent behavior against finance scenarios. The default eval suite
runs in deterministic mode so it is stable in CI and local development.

```bash
python -m evals.run_evals
```

Expected output:

```text
3/3 evals passed
txn_1007_missing_acceptance: PASS score=1.00
txn_1012_subscription_ready: PASS score=1.00
missing_transaction_escalates: PASS score=1.00
```

Use JSON output for automation:

```bash
python -m evals.run_evals --json
```

## Run API

```bash
uvicorn app.main:app --reload
```

Then open:

```text
http://localhost:8000/docs
```

## Run Chat UI

```bash
cd frontend
pnpm install
pnpm dev
```

Then open:

```text
http://localhost:5173
```

## Run With Docker

```bash
docker compose up --build
```

## Example Request

```bash
curl -X POST http://localhost:8000/agent/review-transaction \
  -H "Content-Type: application/json" \
  -d "{\"transaction_id\":\"txn_1007\",\"company_id\":\"acme\"}"
```

Expected decision: `escalate`, because the transaction requires customer
acceptance evidence and that evidence is missing.

## Legacy Mock Exercise

The original minimal interview exercise still lives in `agent.py` and
`test_agent.py`. It demonstrates the lower-level tool-calling loop mechanics:

- parse tool-call JSON arguments
- execute requested tools
- preserve tool call IDs
- return JSON tool outputs
- handle multiple tool calls and unknown tools
