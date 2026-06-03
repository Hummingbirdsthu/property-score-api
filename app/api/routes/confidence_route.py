from fastapi import APIRouter
from typing import Any, Dict
from app.services.confidence_service import (
    confidence_score_api
)

router = APIRouter(
    prefix="/api/confidence",
    tags=["Confidence"]
)

@router.post("/score")
def get_confidence_score(data: Dict[str, Any]):
    result = confidence_score_api(data)

    return {
        "success": True,
        "data": result
    }