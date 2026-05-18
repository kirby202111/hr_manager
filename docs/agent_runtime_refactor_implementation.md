# Agent Runtime Refactor Implementation

Date: 2026-05-18

This note records the current implementation state after the agent runtime refactor.

## Boundary

- `app/models` remains business-domain only.
- `app/agent/models` now owns agent runtime persistence.
- Agent runtime models are not exported through `app.models.__all__`.

## Implemented Runtime Layers

The agent runtime now has its own companion layers:

- `app/agent/models`
- `app/agent/schemas`
- `app/agent/repositories`
- `app/agent/services`

## Runtime Models

Implemented runtime entities:

- `AgentMemory`
- `MemoryReminder`
- `ConversationMessage`

## Constraints Followed

- No `ForeignKey(...)` in agent runtime models.
- Memory-to-reminder relationship uses explicit ORM join expressions.
- Runtime conversation history persists outside the business-domain model boundary.
- `main.py` explicitly imports both business ORM models and agent runtime ORM models for table registration.

## Runtime Skills

The rewritten runtime currently registers these skills:

- `workforce`
- `attendance`
- `capability`
- `collaboration`
- `knowledge_base`
- `memory`

## Verification

Validated with:

```bash
uv run ruff check app/agent main.py --no-cache
uv run python -c "import main; print('ok')"
```
