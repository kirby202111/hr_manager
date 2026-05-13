# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend
```bash
# Run dev server (hot reload)
uvicorn main:app --reload

# Seed database with sample data
python scripts/seed_data.py

# Seed knowledge base
python scripts/seed_knowledge_base.py

# Install dependencies (uses uv)
uv pip install
```

### Frontend
```bash
cd frontend
npm install
npm run dev      # Dev server at http://localhost:5173
npm run build    # Production build
```

## Architecture

This is an HR management system with a FastAPI backend and Vue 3 frontend. The backend follows a strict 4-layer architecture where every new feature must touch all layers:

```
Router → Service → Repository → Model
```

- **Model** (`app/models/`): SQLAlchemy 2.0 ORM models using `Mapped` + `mapped_column`. All inherit from `Base` (in `app/database.py`) and use `_to_dict` from `app/models/base.py` for serialization. No foreign key constraints — relationships are by integer ID only.
- **Repository** (`app/repositories/`): Raw database operations. Each function opens its own `SessionLocal()` context. Returns `dict | None` via `model.to_dict()`.
- **Service** (`app/services/`): Business logic, validation, and HTTPException raising. Calls repositories and enriches responses (e.g., filling `employee_name` from employee repo). Returns Pydantic response models.
- **Router** (`app/routers/`): Thin FastAPI `APIRouter` endpoints that delegate to services. Uses `response_model` for automatic serialization.
- **Schema** (`app/schemas/`): Pydantic models for each entity: `{Entity}Create`, `{Entity}Update`, `{Entity}Response`, `{Entity}ListResponse` (with `items`/`total`).

New models must be registered in `app/models/__init__.py` and new routers in `main.py`.

## AI Agent System

The backend includes a ReAct agent that lets users interact with HR data through natural language chat (`/agent/chat` and `/agent/chat/stream`).

### Agent Request Flow
1. User message hits `/agent/chat` → `ReActAgent.chat()`
2. If `USE_SKILL_ROUTING=true`, the `SkillRouter` uses the LLM to select relevant skills
3. The agent calls the LLM (DeepSeek) with system prompt, conversation history, and available tools
4. LLM responds with tool calls → agent executes them → feeds results back to LLM
5. Loop continues until LLM returns a final answer or `AGENT_MAX_ITERATIONS` is reached

### Adding a New Skill
1. Create `app/agent/skills/{name}.py` — define a `Skill` object with `AgentTool` entries
2. Each tool wraps a service function via `_safe()` (handles HTTPException → `{"error": detail}`)
3. Import and add to `_ALL_SKILLS` in `app/agent/skills/__init__.py`

Skill tools call service-layer functions directly (not routers). Create/update tools must construct Pydantic schema objects before passing to service.

### Key Agent Files
- `app/agent/protocol.py` — `AgentTool`, `Skill`, `_safe()` wrapper
- `app/agent/react_agent.py` — ReAct loop implementation
- `app/agent/skill_registry.py` — skill registration, tool resolution
- `app/agent/skill_router.py` — LLM-based skill selection
- `app/agent/history.py` — in-memory conversation history

## Knowledge Base

ChromaDB vector store for HR document search. Uses DashScope (Aliyun) for text embeddings. Configured via `KNOWLEDGE_BASE_*` env vars. Seeded separately via `scripts/seed_knowledge_base.py`.

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy 2.0, SQLite, Pydantic v2
- **AI**: DeepSeek API (OpenAI-compatible client), DashScope embeddings, ChromaDB
- **Frontend**: Vue 3, TypeScript, Vite, Element Plus, Pinia, Axios
- **Python**: >= 3.13, managed with uv

## Conventions

- All API responses are in Chinese (tags, error messages, field names where user-facing)
- Proficiency levels use English enum values: `beginner`, `intermediate`, `advanced`, `expert`
- List endpoints return `{entities: [...], total: int}` pattern
- No database migrations — `Base.metadata.create_all()` runs on startup; use `seed_data.py` to reset
