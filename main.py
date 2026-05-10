from fastapi import FastAPI

from app.routers import employee, department, attendance, leave, payroll, performance

app = FastAPI(title="员工管理系统 API", version="2.0.0")

app.include_router(employee.router)
app.include_router(department.router)
app.include_router(attendance.router)
app.include_router(leave.router)
app.include_router(payroll.router)
app.include_router(performance.router)


@app.get("/")
def read_root():
    return {"message": "员工管理系统 API v2.0"}
