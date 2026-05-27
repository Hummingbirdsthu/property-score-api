from typing import Any, Dict
from app.utils.ppss import (calculate_f_score, calculate_P_by_f_score, flatten )


def calculate_single_asset_score(data: Dict[str, Any]):
    asset = flatten(data)
    score = calculate_f_score(asset)

    return {
        "f_score": round(score, 4)
    }


def calculate_compare_price(data: Dict[str, Any]):
    result = calculate_P_by_f_score(data)
    return result