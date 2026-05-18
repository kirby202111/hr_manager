from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agent.models import *  # noqa: F403 - register agent runtime ORM tables
from app.agent.router import create_agent
from app.agent.router import router as agent_router
from app.errors import AppError, app_error_handler
from app.models import *  # noqa: F403 - register business ORM tables
from app.routers import (
    attendance,
    capability,
    organization,
    production,
    qualification,
    risk,
    shopfloor,
    staffing,
    workforce,
)
from app.schema import initialize_database


@asynccontextmanager
async def lifespan(_app: FastAPI):
    initialize_database()
    _app.state.agent, _app.state.skill_registry, _app.state.history_store = create_agent()
    yield


app = FastAPI(title="Workforce Ops API", version="2.0.0", lifespan=lifespan)

app.add_exception_handler(AppError, app_error_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(organization.router)
app.include_router(workforce.router)
app.include_router(capability.router)
app.include_router(qualification.router)
app.include_router(shopfloor.router)
app.include_router(production.router)
app.include_router(risk.router)
app.include_router(staffing.router)
app.include_router(attendance.router)
app.include_router(agent_router)


@app.get("/")
def read_root():
    return {"message": "Workforce Ops API v2.0"}
