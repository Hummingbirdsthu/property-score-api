"""
Tính độ tin cậy (Confidence Score) cho kết quả định giá AVM.
Đầu vào: JSON output của calculate_P_by_f_score(sample)
"""

from datetime import datetime, date
from typing import Optional
from ppss import calculate_P_by_f_score


# ---------------------------------------------------------------------------
# 1. Số lượng TSSS hợp lệ
# ---------------------------------------------------------------------------

def score_so_luong(n: int) -> int:
    if n >= 5:
        return 100
    elif n >= 3:
        return 95
    elif n == 2:
        return 90
    elif n == 1:
        return 80
    else:
        return 45


# ---------------------------------------------------------------------------
# 2. Khoảng cách trung bình 3 TSSS gần nhất (đơn vị: mét)
# ---------------------------------------------------------------------------

def score_khoang_cach(avg_distance_m: float) -> int:
    if avg_distance_m <= 300:
        return 100
    elif avg_distance_m <= 500:
        return 95
    elif avg_distance_m <= 1000:
        return 90
    elif avg_distance_m <= 2000:
        return 80
    else:
        return 45


# ---------------------------------------------------------------------------
# 3. Thời gian giao dịch trung bình 3 TSSS gần nhất (đơn vị: ngày)
# ---------------------------------------------------------------------------

def score_thoi_gian(avg_days: float) -> int:
    if avg_days <= 30:
        return 100
    elif avg_days <= 90:
        return 95
    elif avg_days <= 180:
        return 85
    elif avg_days <= 365:
        return 70
    elif avg_days <= 730:
        return 50
    else:
        return 25


# ---------------------------------------------------------------------------
# 4. Nguồn dữ liệu
# ---------------------------------------------------------------------------

SOURCE_SCORE = {
    "cong_chung":       100,
    "registry":         100,
    "core_banking":     95,
    "third_party":      90,
    "khung_gia":        90,
    "listing":          85,
    "user_input":       80,
}

def score_nguon(source: str) -> int:
    """
    source: một trong các key của SOURCE_SCORE.
    Nếu không khớp trả về 80 (mức thấp nhất đã biết).
    """
    return SOURCE_SCORE.get(source.lower(), 85)


# ---------------------------------------------------------------------------
# 5. Biên giá (spread = (Pmax - Pmin) / Pavg * 100)
# ---------------------------------------------------------------------------

def score_bien_gia(spread_pct: float) -> int:
    if spread_pct <= 5:
        return 100
    elif spread_pct <= 10:
        return 90
    elif spread_pct <= 15:
        return 80
    elif spread_pct <= 20:
        return 65
    elif spread_pct <= 30:
        return 45
    else:
        return 20


def calc_spread(p_list: list[float]) -> float:
    """Tính spread (%) từ danh sách giá."""
    valid = [p for p in p_list if p is not None]
    if len(valid) == 1:
        return valid
    pmax, pmin, pavg = max(valid), min(valid), sum(valid) / len(valid)
    return (pmax - pmin) / pavg * 100 if pavg else 0


# ---------------------------------------------------------------------------
# 6. Overall Confidence Score
# ---------------------------------------------------------------------------

WEIGHTS = {
    "so_luong":   0.15,
    "khoang_cach": 0.25,
    "thoi_gian":  0.25,
    "nguon":      0.20,
    "bien_gia":   0.15,
}

def overall_confidence(scores: dict) -> float:
    """scores: dict với các key trùng WEIGHTS."""
    return sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)


# ---------------------------------------------------------------------------
# 7. Confidence Grade
# ---------------------------------------------------------------------------

def grade(cs: float) -> tuple[str, str]:
    if cs >= 90:
        return "A", "Rất tin cậy"
    elif cs >= 80:
        return "B", "Tốt"
    elif cs >= 70:
        return "C", "Chấp nhận được"
    elif cs >= 50:
        return "D", "Rủi ro"
    else:
        return "E", "Không khuyến nghị"


# ---------------------------------------------------------------------------
# 8. Warning Engine
# ---------------------------------------------------------------------------

def warnings(n_tsss: int, avg_distance_m: float, avg_days: float,
              spread_pct: float, source_score: int) -> list[str]:
    msgs = []
    if n_tsss < 3:
        msgs.append("Không đủ comparable (TSSS < 3)")
    if avg_distance_m > 2000:
        msgs.append("Comparables quá xa (Avg Distance > 2km)")
    if avg_days > 365:
        msgs.append("Giao dịch quá cũ (Avg Time > 1 năm)")
    if spread_pct > 20:
        msgs.append("Giá thị trường biến động mạnh (Spread > 20%)")
    if source_score < 50:
        msgs.append("Dữ liệu không đáng tin (Data Source score < 50)")
    return msgs

# Helper: tính số ngày từ transaction_date đến hôm nay
def days_since(transaction_date) -> float:
    """
    transaction_date: str ISO (YYYY-MM-DD), date, hoặc datetime.
    Trả về số ngày tính đến hôm nay.
    """
    if isinstance(transaction_date, str):
        transaction_date = date.fromisoformat(transaction_date[:10])
    if isinstance(transaction_date, datetime):
        transaction_date = transaction_date.date()
    return (date.today() - transaction_date).days


# ---------------------------------------------------------------------------
# Hàm chính
# ---------------------------------------------------------------------------
def calculate_confidence(data: dict) -> dict:
    """
    Đầu vào: output của calculate_P_by_f_score(sample) — đã có f_tsmt, f_tsss, P_tsmt.

    Mỗi asset trong comparable_assets cần có thêm:
        - distance_m       : khoảng cách tới TSMT (mét)
        - transaction_date : ngày giao dịch (str ISO hoặc date)
        - data_source      : nguồn dữ liệu (xem SOURCE_SCORE)

    Trả về dict gốc được bổ sung thêm key "confidence".
    """
    comps = data.get("comparable_assets", [])
    n = len(comps)
    comps_with_dist = [c for c in comps if c.get("distance_m") is not None]
    
    # 1. Số lượng
    k_so_luong = score_so_luong(n)

    # 2. khoang cach
    avg_dist = sum(c["distance_m"] for c in comps_with_dist) / len(comps_with_dist)
    k_khoang_cach = score_khoang_cach(avg_dist)

    # 3. Thời gian trung bình 
    ages = []
    for c in (comps_with_dist if comps_with_dist else comps):
        td = c.get("transaction_date")
        if td:
            ages.append(days_since(td))
    avg_days = sum(ages) / len(ages) if ages else 0.0
    k_thoi_gian = score_thoi_gian(avg_days)

    # 4. Nguồn dữ liệu — lấy nguồn phổ biến nhất hoặc trung bình
    source_scores = []
    for c in comps:
        src = c.get("data_source")
        if src:
            source_scores.append(score_nguon(src))
    k_nguon = round(sum(source_scores) / len(source_scores)) if source_scores else 85

    # 5. Biên giá từ P_tsmt
    p_list = [c.get("P_tsmt") for c in comps]
    spread = calc_spread(p_list)
    k_bien_gia = score_bien_gia(spread)

    # 6. Overall CS
    scores = {
        "so_luong":    k_so_luong,
        "khoang_cach": k_khoang_cach,
        "thoi_gian":   k_thoi_gian,
        "nguon":       k_nguon,
        "bien_gia":    k_bien_gia,
    }
    cs = overall_confidence(scores)
    cs_grade, cs_meaning = grade(cs)

    # 7. Warnings
    warns = warnings(n, avg_dist, avg_days, spread, k_nguon)

    # --- Gắn kết quả vào data gốc ---
    confidence = {
        "overall_score": round(cs, 2),
        "grade": cs_grade,
        "meaning": cs_meaning,
        "component_scores": {
            "so_luong_tsss":  {"score": k_so_luong,    "weight": "15%", "n": n},
            "khoang_cach":    {"score": k_khoang_cach, "weight": "25%", "avg_distance_m": round(avg_dist, 1)},
            "thoi_gian":      {"score": k_thoi_gian,   "weight": "25%", "avg_days": round(avg_days, 1)},
            "nguon_du_lieu":  {"score": k_nguon,        "weight": "20%"},
            "bien_gia":       {"score": k_bien_gia,     "weight": "15%", "spread_pct": round(spread, 2)},
        },
        "warnings": warns,
    }
    return confidence


# ---------------------------------------------------------------------------
# Demo / quick-test
# ---------------------------------------------------------------------------

# if __name__ == "__main__":
#     import json
#     sample_output = {
#     "target_asset": {
#         "asset_id": "TSMT_001",
#         "property_type": "Nhà riêng",
#         #"price": null,
#         "area": 74,
#         "road_width": 4,
#         "length": 18,
#         "legal": "sổ đỏ/sổ hồng",
#         "address": "Chu Văn An, P12, Bình Thạnh",
#         "ward": "Phường 12",
#         "district": "Bình Thạnh",
#         "city": "Hồ Chí Minh",
#         "lat": 10.81095064,
#         "lng": 106.701879,
#         "alley_width": 6,
#         "alley_level": 1,
#         "alley_type": "thông",
#         "floors": 2,
#         # "house_direction": null,
#         # "features": {
#         #   "is_corner": false,
#         #   "is_wide_alley": true,
#         #   "is_full_furniture": true,
#         #   "is_new_house": true,
#         #   "is_business_good": true
#         # },
#         "nearby": {
#         "school": 167,
#         "hospital": 781,
#         "market": 711,
#         "airport": 5107,
#         "railway": 1959,
#         "landfill": 2204,
#         "pagoda": 582
#         },
#         "note": "Hẻm ô tô - 74m2 - nhà mới full nội thất"
#     },
#     "comparable_assets": [
#         {
#         "asset_id": "TSSS_001",
#         "price": 18000000000,
#         "area": 330,
#         "address": "Chu Văn An, P12",
#         "lat": 10.81078753,
#         "lng": 106.7019831,
#         "nearby": {
#             "school": 180.8,
#             "hospital": 792.5,
#         "market": 724,
#             "airport": 5121.4,
#             "railway": 1975.2,
#             "landfill": 2200.2,
#             "pagoda": 594.2
#         },
#         "distance_m": 375,
#         "note": "Nhà chính chủ cần bán gấp"
#         },
#         {
#         "asset_id": "TSSS_002",
#         "price": 6200000000,
#         "area": 36,
#         "address": "Chu Văn An, P12",
#         "lat": 10.81069242,
#         "lng": 106.7017343,
#         "nearby": {
#             "school": 199.5,
#             "hospital": 765.6,
#             "market": 697.6,
#             "airport": 5096.3,
#             "railway": 1952.3,
#             "landfill": 2229.4,
#             "pagoda": 567.6
#         },
#         "distance_m": 365.23009145,
#         "note": "Nhà mới 2 tầng - nở hậu"
#         },
#         {
#         "asset_id": "TSSS_003",
#         "price": 9700000000,
#         "area": 74,
#         "address": "Chu Văn An, P12",
#         "lat": 10.81095064,
#         "lng": 106.701879,
#         "nearby": {
#             "school": 167,
#             "hospital": 781.1,
#             "market": 711.7,
#             "airport": 5107.3,
#             "railway": 1959.2,
#             "landfill": 2204.9,
#             "pagoda": 582.1
#         },
#         "distance_m": 344.02104631,
#         "note": "Hẻm ô tô - nhà mới full nội thất"
#         }
#     ]
#     }

#     sample_output = calculate_P_by_f_score(sample_output)
#     print(json.dumps(sample_output, ensure_ascii=False, indent=2))
#     result = calculate_confidence(sample_output)
#     print(json.dumps(result, ensure_ascii=False, indent=2))