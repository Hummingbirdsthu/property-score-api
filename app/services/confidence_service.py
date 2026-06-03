from typing import Any, Dict
from app.utils.confidence import (calculate_confidence )

def confidence_score_api(data: Dict[str, Any]):
    return calculate_confidence(data)
