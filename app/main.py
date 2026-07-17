from fastapi import FastAPI
from app.api.endpoints import (
    ppss_router,
    confidence_router,
    ppcp_router,
    comparative_property_router,
)

app = FastAPI(title="Property Score API")

app.include_router(ppss_router)
app.include_router(confidence_router)
app.include_router(ppcp_router)
app.include_router(comparative_property_router)


@app.get("/")
def home():
    return {"message": "API is running"}
