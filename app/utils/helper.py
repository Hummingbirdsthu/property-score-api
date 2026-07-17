import re
import unicodedata
import math
from typing import Optional


def normalize_text(text: str) -> str:
    """Chuẩn hoá tên phường/đường để so khớp ILIKE trên DB."""
    if not text:
        return ""

    text = unicodedata.normalize("NFC", text)
    text = text.lower()

    replace_words = [
        "thành phố", "tp.",
        "quận", "huyện",
        "phường", "xã",
        "thị trấn",
        "đường", "đ."
    ]

    for w in replace_words:
        text = text.replace(w, " ")

    text = re.sub(r"\s+", " ", text).strip()

    return text


def format_string(s: Optional[str]) -> str:
    if not s:
        return ""
    s = s.lower().strip()
    return re.sub(r"[^a-z0-9\u00c0-\u1ef9]+", "", s)

def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = math.sqrt(sum(a * a for a in v1))
    n2 = math.sqrt(sum(b * b for b in v2))
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)