from fastapi import FastAPI
from app.api.routes.ppss_route import router as ppss_router
from app.api.routes.confidence_route import router as confidence_router

app = FastAPI(title="Property Score API")

app.include_router(ppss_router)
app.include_router(confidence_router)


@app.get("/")
def home():
    return {
        "message": "API is running"
    }