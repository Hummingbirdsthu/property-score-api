from fastapi import APIRouter
from app.services.scoring_service import calculate_score

router = APIRouter(
    prefix="/api",
    tags=["Score"]
)

@router.post("/score")
def score(data: dict):
    result = calculate_score(data)
    return {
        "success": True,
        "score": result
    }