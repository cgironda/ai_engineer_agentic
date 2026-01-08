# Runtime Workflow

This document captures the end-to-end workflow to run the Trading Account backend (FastAPI + Gradio) and the Svelte UI.

![Runtime workflow diagram](assets/runtime_flow.svg)

## Prerequisites
- Python 3.12+
- Node 20.19.6 (via nvm)
- Backend dependencies installed
- UI dependencies installed

## Install Dependencies

### Backend (Python)
```bash
pip install -r /Users/cgironda/projects/Data_Science/AI_Engineer/agentic/crew_prj/dev_team/output_cp/requirements.txt
```

### Frontend (Node)
```bash
cd /Users/cgironda/projects/Data_Science/AI_Engineer/agentic/crew_prj/dev_team/ui
PATH=/Users/cgironda/.nvm/versions/node/v20.19.6/bin:$PATH npm install
```

## Configuration (Optional)
Copy the example env file and adjust values as needed:
```bash
cp /Users/cgironda/projects/Data_Science/AI_Engineer/agentic/crew_prj/dev_team/output_cp/.env.example \
  /Users/cgironda/projects/Data_Science/AI_Engineer/agentic/crew_prj/dev_team/output_cp/.env
```

Common settings:
- `CORS_ORIGINS` (comma-separated list)
- `SESSION_TTL_SECONDS` (defaults to 3600)
- `SERVER_HOST` (defaults to `127.0.0.1`)
- `SERVER_PORT` (defaults to `8000`)
- `SERVER_RELOAD` (defaults to `false`)

## Start the Backend API + Gradio
```bash
cd /Users/cgironda/projects/Data_Science/AI_Engineer/agentic/crew_prj/dev_team/output_cp
uvicorn api:app --host 127.0.0.1 --port 8000
```

## Start the Svelte UI
```bash
cd /Users/cgironda/projects/Data_Science/AI_Engineer/agentic/crew_prj/dev_team/ui
PATH=/Users/cgironda/.nvm/versions/node/v20.19.6/bin:$PATH npm run dev -- --host 127.0.0.1 --port 5173
```

## Verify Runtime
- API health: `http://127.0.0.1:8000/api/health`
- Gradio UI: `http://127.0.0.1:8000/gradio`
- Svelte UI: `http://127.0.0.1:5173/`

## Stop Servers
- Use `CTRL+C` in each terminal, or:
```bash
lsof -ti :8000 :5173 | xargs kill
```
