# Workforce Ops

Workforce Ops is a FastAPI-based backend for manufacturing workforce operations, with a Vue chat frontend and an agent runtime that can call domain services.

## Current Architecture

- `app/models`: business-domain ORM models only
- `app/agent/models`: agent runtime ORM models only
- `app/repositories`: business repositories
- `app/agent/repositories`: agent runtime repositories
- `app/services`: business services
- `app/agent/services`: agent runtime services
- `app/routers`: business REST routers
- `app/agent/router.py`: agent REST and SSE endpoints

The agent runtime keeps its own persistence boundary for:

- long-term memories
- reminder tasks
- conversation messages

These runtime records are not exported through `app.models.__all__`.

## Repository Layout

```text
app/
  agent/
    models/
    repositories/
    schemas/
    services/
    skills/
    history.py
    react_agent.py
    router.py
    skill_registry.py
    skill_router.py
  knowledge_base/
  models/
  repositories/
  routers/
  schemas/
  services/
frontend/
migrations/
main.py
```

## Agent Endpoints

- `POST /agent/chat`
- `POST /agent/chat/stream`
- `GET /agent/sessions`
- `GET /agent/sessions/{session_id}/messages`
- `DELETE /agent/sessions/{session_id}`
- `GET /agent/skills`
- `POST /agent/skills/{skill_name}/enable`
- `POST /agent/skills/{skill_name}/disable`

## Registered Agent Skills

The runtime currently registers these skills:

- `workforce`
- `attendance`
- `capability`
- `collaboration`
- `knowledge_base`
- `memory`

## Agent Runtime Data Model

`app/agent/models` contains:

- `AgentMemory`
- `MemoryReminder`
- `ConversationMessage`

Design constraints followed by the implementation:

- no `ForeignKey(...)` usage in agent runtime models
- explicit ORM joins for runtime relationships
- runtime models separated from business-domain models
- runtime schemas live under `app/agent/schemas`
- runtime repositories and services live under `app/agent/repositories` and `app/agent/services`

## Run Locally

### Backend

```bash
uv sync --dev
alembic upgrade head
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Backend default URL:

- `http://localhost:8000`

Frontend default URL:

- `http://localhost:5173`

## Configuration

Runtime configuration is defined in `app/config.py`.

Key settings include:

- `DATABASE_URL`
- `DEEPSEEK_API_KEY`
- `DEEPSEEK_BASE_URL`
- `DEEPSEEK_MODEL`
- `AGENT_MAX_ITERATIONS`
- `AGENT_MAX_HISTORY_MESSAGES`
- `USE_SKILL_ROUTING`
- `DEFAULT_USER_TAG`
- `DASHSCOPE_API_KEY`
- `DASHSCOPE_BASE_URL`
- `DASHSCOPE_EMBEDDING_MODEL`
- `KNOWLEDGE_BASE_DIR`
- `KNOWLEDGE_BASE_CHUNK_SIZE`
- `KNOWLEDGE_BASE_CHUNK_OVERLAP`
- `KNOWLEDGE_BASE_SEARCH_TOP_K`

## Validation

Useful checks:

```bash
uv run ruff check app/agent main.py --no-cache
uv run python -c "import main; print('ok')"
```
