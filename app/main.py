from fastapi import FastAPI
from app.api.routes.ppss_route import router as ppss_router

app = FastAPI(title="Property Score API")

app.include_router(ppss_router)


@app.get("/")
def home():
    return {
        "message": "API is running"
    }