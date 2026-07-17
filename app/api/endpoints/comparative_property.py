from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.response import BaseResponseSchema
from app.services.comparative_property_service import ComparativePropertyService


router = APIRouter(
    prefix="/api/v1/compare-property",
    tags=["Comparative Property"]
)


@router.post("/")
def get_compare_property(data: dict, db: Session = Depends(get_db)):
    cpService = ComparativePropertyService(db)
    try:
        result = cpService.find(property_target=data)
        return BaseResponseSchema(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")