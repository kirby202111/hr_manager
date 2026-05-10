from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.models import orm  # noqa: F401
from app.routers import employee, department, attendance, leave, payroll, performance
from app.agent import router as agent_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="员工管理系统 API", version="2.0.0", lifespan=lifespan)

app.include_router(employee.router)
app.include_router(department.router)
app.include_router(attendance.router)
app.include_router(leave.router)
app.include_router(payroll.router)
app.include_router(performance.router)
app.include_router(agent_router.router)


@app.get("/")
def read_root():
    return {"message": "员工管理系统 API v2.0"}
