from fastapi import FastAPI

from app.routers import items

app = FastAPI(title="My API", version="1.0.0")

app.include_router(items.router)


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
