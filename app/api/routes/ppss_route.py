from fastapi import APIRouter
from typing import Any, Dict
from app.services.ppss_service import (
    calculate_compare_price
)

router = APIRouter(
    prefix="/api/ppss",
    tags=["PPSS"]
)

@router.post("/compare-price")
def get_compare_price(data: Dict[str, Any]):
    result = calculate_compare_price(data)

    return {
        "success": True,
        "data": result
    }