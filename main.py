from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.models import *  # noqa: F403 — register all ORM tables
from app.routers import employee, department, attendance, leave, payroll, performance
from app.agent.router import create_agent


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _app.state.agent, _app.state.skill_registry, _app.state.history_store = create_agent()
    yield


app = FastAPI(title="员工管理系统 API", version="2.0.0", lifespan=lifespan)

app.include_router(employee.router)
app.include_router(department.router)
app.include_router(attendance.router)
app.include_router(leave.router)
app.include_router(payroll.router)
app.include_router(performance.router)

from app.agent.router import router as agent_router
app.include_router(agent_router)


@app.get("/")
def read_root():
    return {"message": "员工管理系统 API v2.0"}
