from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agent.router import create_agent
from app.agent.router import router as agent_router
from app.errors import AppError, app_error_handler
from app.models import *  # noqa: F403 — register all ORM tables
from app.routers import (
    attendance,
    capability,
    collaboration,
    organization,
    qualification,
    shopfloor,
    staffing,
    workforce,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _app.state.agent, _app.state.skill_registry, _app.state.history_store = create_agent()
    yield


app = FastAPI(title="员工管理系统 API", version="2.0.0", lifespan=lifespan)

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
app.include_router(staffing.router)
app.include_router(attendance.router)
app.include_router(collaboration.router)
app.include_router(agent_router)


@app.get("/")
def read_root():
    return {"message": "员工管理系统 API v2.0"}
