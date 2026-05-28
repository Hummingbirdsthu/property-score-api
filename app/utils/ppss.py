from __future__ import annotations
from typing import Union, Optional


# ---------------------------------------------------------------------------
# Bảng tra cứu
# ---------------------------------------------------------------------------

# 1.1. road_type – giá trị là string
ROAD_TYPE_TABLE: dict[str, float] = {
    "CBD":       1.00,
    "Trục chính": 0.85,
    "Khu vực":   0.70,
    "Nội khu":   0.55,
    "Đường nhỏ": 0.30,
}
ROAD_TYPE_W = 0.25

# 1.2. road_width – giá trị là số (mét), so sánh theo ngưỡng giảm dần
# Mỗi phần tử: (ngưỡng_tối_thiểu, K)
ROAD_WIDTH_BREAKS: list[tuple[float, float]] = [
    (20,  1.00),   # >20m
    (13,  0.95),   # 13–20m
    (9,   0.90),   # 9–13m
    (7,   0.85),   # 7–9m
    (5,   0.75),   # 5–7m
    (0,   0.40),   # <5m
]
ROAD_WIDTH_W = 0.20

# 1.3. poi_density – giá trị là số nguyên
POI_DENSITY_BREAKS: list[tuple[float, float]] = [
    (25, 1.00),   # ≥25
    (15, 0.80),   # 15–25
    (5,  0.60),   # 5–15
    (1,  0.40),   # 1–5
    (0,  0.20),   # 0
]
POI_DENSITY_W = 0.15

# 1.4. amenity – giá trị là số nhóm (0–4+)
AMENITY_BREAKS: list[tuple[float, float]] = [
    (4, 1.00),   # ≥4 nhóm
    (3, 0.80),   # 3 nhóm
    (2, 0.60),   # 2 nhóm
    (1, 0.40),   # 1 nhóm
    (0, 0.20),   # 0 nhóm
]
AMENITY_W = 0.10

# 1.5. sidewalk – giá trị là số (mét)
SIDEWALK_BREAKS: list[tuple[float, float]] = [
    (2, 1.00),   # >2m
    (0.001, 0.70),   # <2m (>0)
    (0, 0.40),   # 0 (không có)
]
SIDEWALK_W = 0.10

# 2.1. alley_cap  – giá trị là số nhóm (1–4)
ALLEY_CAP_BREAKS: list[tuple[float, float]] = [
    (1, .9),   # 1 nhóm
    (2, 0.75),   # 2 nhóm
    (3, 0.60),   # 3 nhóm
    (4, 0.45),   # 4 nhóm
]
ALLEY_CAP_W = 0.4

# 2.2. distance_main – giá trị là số (mét)
DISTANCE_MAIN_BREAKS: list[tuple[float, float]] = [
    (500, 0.50),   # >500m
    (200, 0.70),   # 200-500m 
    (50, 0.85),    # 50-200m 
    (0, 1),        # # >500m
]
DISTANCE_MAIN_W = 0.25

# 2.3. alley_level  – giá trị là số nhóm (1–4+)
ALLEY_LEVEL_BREAKS: list[tuple[float, float]] = [
    (4, .65),   # ≥4 nhóm
    (3, 0.8),   # 3 nhóm
    (2, 0.9),   # 2 nhóm
    (1, 1),   # 1 nhóm
]
ALLEY_LEVEL_W = 0.15

# 2.4. alley_type – giá trị là string
ALLEY_TYPE_TABLE: dict[str, float] = {
    "thông":    1.00,
    "cụt":      0.85,
}
ALLEY_TYPE_W = 0.1

# 2.5. alley_quality  – giá trị là string
ALLEY_QUALITY_TABLE: dict[str, float] = {
    "Tốt":          1.00,
    "Trung bình":   0.9,
    "Kém":          0.75,
    "Ngập":         0.6,
}
ALLEY_QUALITY_W = 0.1

# 3.1. Diện tích – giá trị là số (mét vuông)
LAND_AREA_BREAKS: list[tuple[float, float]] = [
    (120, 0.90),    # >120m²
    (80, 1),        # 80–120m²
    (60, 0.95),     # 60–<80m²
    (40, 0.90),     # 40–<60m²
    (0, 0.75),      # <40m²
]
LAND_AREA_W = 0.15

# 3.2. shape – giá trị là string
SHAPE_TABLE: dict[str, float] = {
    "Vuông":    1.00,
    "Méo":      0.9,
    "Gãy khúc": 0.75,
}
SHAPE_W = 0.1

# 3.3. ratio - 


# 3.4. 
REAR_SHAPE_TABLE: dict[str, float] = {
    "Nở hậu":    1.05,
    "Vuông":      1.00,
    "Thóp nhẹ":  0.90,
    "Thóp mạnh": 0.75,
}
REAR_SHAPE_W = 0.10

# 3.5. Mặt tiền
FRONTAGE_WIDTH_BREAKS: list[tuple[float, float]] = [
    (10, 1.10),   # >10m
    (6,  1.05),   # 6–10m
    (4,  1.00),   # 4–<6m
    (3,  0.85),   # 3–<4m
    (0,  0.70),   # <3m
]
FRONTAGE_WIDTH_W = 0.15
 
# 3.6. Mặt tiền
FRONTAGE_COUNT_BREAKS: list[tuple[float, float]] = [
    (2, 1.10),   # ≥2 MT
    (1, 1.00),   # 1 MT
]
FRONTAGE_COUNT_W = 0.10
 
# 3.7. Công trình
FLOOR_AREA_BREAKS: list[tuple[float, float]] = [
    (400, 1.10),   # >400m²
    (250, 1.05),   # 250–400m²
    (150, 1.00),   # 150–250m²
    (80,  0.90),   # 80–150m²
    (0,   0.80),   # <80m²
]
FLOOR_AREA_W = 0.10
 
# 3.8. Công trình
BUILDING_GRADE_TABLE: dict[str, float] = {
    "Cấp 1":   1.05,
    "Cấp 2":   1.00,
    "Cấp 3":   0.90,
    "Cấp 4":   0.80,
    "Nhà tạm": 0.60,
}
BUILDING_GRADE_W = 0.15
 
 # 4.1. school – d (m)
SCHOOL_BREAKS: list[tuple[float, float]] = [
    (0,   1.12),   # d ≤ 100m
    (100, 1.10),   # 100–300m
    (300, 1.00),   # 300–700m
    (700, 0.95),   # >700m
]
SCHOOL_W = 0.18

# 4.2. hospital – d (m); ≤50m được coi là quá gần → K thấp hơn
HOSPITAL_BREAKS: list[tuple[float, float]] = [
    (0,   0.98),   # d ≤ 50m
    (50,  1.05),   # 50–200m
    (200, 1.00),   # 200–500m
    (500, 0.95),   # >500m
]
HOSPITAL_W = 0.14

# 4.3. mall – d (m)
MALL_BREAKS: list[tuple[float, float]] = [
    (0,    1.12),   # ≤200m
    (200,  1.08),   # 200–500m
    (500,  1.00),   # 500–1000m
    (1000, 0.95),   # >1000m
]
MALL_W = 0.08

# 4.4. supermarket – d (m)
SUPERMARKET_BREAKS: list[tuple[float, float]] = [
    (0,   1.08),   # d ≤ 100m
    (100, 1.05),   # 100–300m
    (300, 1.00),   # 300–800m
    (800, 0.95),   # >800m
]
SUPERMARKET_W = 0.07

# 4.5. metro – d (m); <100m không có mức riêng → dùng mức 100–500m
METRO_BREAKS: list[tuple[float, float]] = [
    (0,    1.15),   # 100–500m  (gộp <100 vào đây vì không có mức riêng)
    (500,  1.10),   # 500–1000m
    (1000, 1.00),   # 1–2km
    (2000, 0.95),   # >2km
]
METRO_W = 0.13

# 4.6. park – d (m)
PARK_BREAKS: list[tuple[float, float]] = [
    (0,   1.10),   # d ≤ 100m
    (100, 1.08),   # 100–300m
    (300, 1.00),   # 300–800m
    (800, 0.95),   # >800m
]
PARK_W = 0.10

# 4.7. cbd distance – d (m)
CBD_DIST_BREAKS: list[tuple[float, float]] = [
    (0,    1.15),   # ≤1km
    (1000, 1.10),   # 1–3km
    (3000, 1.00),   # 3–5km
    (5000, 0.95),   # >5km
]
CBD_DIST_W = 0.10

# 4.8. admin_center – d (m); 200–500m là ngưỡng tốt nhất
ADMIN_CENTER_BREAKS: list[tuple[float, float]] = [
    (0,   1.05),   # ≤200m
    (200, 1.10),   # 200–500m
    (500, 1.00),   # 500–1500m
    (1500, 0.95),  # >1500m
]
ADMIN_CENTER_W = 0.04

# 4.9. market – d (m); ≤50m quá ồn → K thấp hơn
MARKET_BREAKS: list[tuple[float, float]] = [
    (0,   0.95),   # ≤50m
    (50,  1.05),   # 50–150m
    (150, 1.10),   # 150–300m
    (300, 1.00),   # 300–700m
    (700, 0.95),   # >700m
]
MARKET_W = 0.04

# 4.10. view – string: "river" | "sea" | None/other → K và W
VIEW_TABLE: dict[str, float] = {
    "Sông":   1.15,
    "Biển":   1.20,
    "Không":  1,
}
VIEW_W = 0.12

# 5.1. landfill – d (m)
LANDFILL_BREAKS: list[tuple[float, float]] = [
    (0,   0.50),   # d ≤ 50
    (50,  0.65),   # 50–100
    (100, 0.80),   # 100–200
    (200, 0.90),   # 200–500
    (500, 1.00),   # >500
]
LANDFILL_W = 0.22

# 5.2. wastewater – d (m)
WASTEWATER_BREAKS: list[tuple[float, float]] = [
    (0,   0.70),   # d ≤ 50
    (50,  0.80),   # 50–150
    (150, 0.90),   # 150–300
    (300, 1.00),   # >300
]
WASTEWATER_W = 0.10

# 5.3. airport – d (m)
AIRPORT_BREAKS: list[tuple[float, float]] = [
    (0,    0.65),   # d ≤ 200
    (200,  0.75),   # 200–500
    (500,  0.85),   # 500–1000
    (1000, 0.92),   # 1000–2000
    (2000, 1.00),   # >2000
]
AIRPORT_W = 0.14

#  5.4. railway – d (m)
RAILWAY_BREAKS: list[tuple[float, float]] = [
    (0,   0.70),   # d ≤ 30
    (30,  0.80),   # 30–100
    (100, 0.88),   # 100–300
    (300, 0.95),   # 300–700
    (700, 1.00),   # >700
]
RAILWAY_W = 0.10

#  5.5. emetery – d (m)
CEMETERY_BREAKS: list[tuple[float, float]] = [
    (0,   0.70),   # d ≤ 50
    (50,  0.80),   # 50–150
    (150, 0.90),   # 150–300
    (300, 1.00),   # >300
]
CEMETERY_W = 0.12

#  5.6. funeral_home – d (m)
FUNERAL_HOME_BREAKS: list[tuple[float, float]] = [
    (0,   0.80),   # d ≤ 50
    (50,  0.85),   # 50–100
    (100, 0.92),   # 100–200
    (200, 1.00),   # >200
]
FUNERAL_HOME_W = 0.06

#  5.7. temple – d (m)
TEMPLE_BREAKS: list[tuple[float, float]] = [
    (0,   0.85),   # d ≤ 50
    (50,  0.90),   # 50–150
    (150, 0.95),   # 150–300
    (300, 1.00),   # >300
]
TEMPLE_W = 0.06

# ---------------------------------------------------------------------------
# Hàm tra cứu chung
# ---------------------------------------------------------------------------

def _lookup_by_threshold(value: float, breaks: list[tuple[float, float]]) -> float:
    """
    Trả về K tương ứng với ngưỡng đầu tiên mà value >= ngưỡng đó.
    breaks phải được sắp xếp giảm dần theo ngưỡng.
    """
    for threshold, k in breaks:
        if value >= threshold:
            return k
    # fallback: trả về K = 0
    return 0

def _score(value, weight: float, lookup_fn) -> float:
    if value is None:
        return 0.0
    return lookup_fn(value) * weight

# ---------------------------------------------------------------------------
# Hàm tính điểm từng feature
# ---------------------------------------------------------------------------

def score_road_type(value: str) -> float:
    if value is None:
        return 0
    k = ROAD_TYPE_TABLE.get(value)
    if k is None:
        return 0
    return k * ROAD_TYPE_W

def score_road_width(value) -> float:
    return _score(value, ROAD_WIDTH_W, lambda v: _lookup_by_threshold(float(v), ROAD_WIDTH_BREAKS))

def score_poi_density(value) -> float:
    return _score(value, POI_DENSITY_W, lambda v: _lookup_by_threshold(float(v), POI_DENSITY_BREAKS))

def score_amenity(value) -> float:
    return _score(value, AMENITY_W, lambda v: _lookup_by_threshold(float(v), AMENITY_BREAKS))

def score_alley_cap(value) -> float:
    return _score(value, AMENITY_W, lambda v: _lookup_by_threshold(float(v), AMENITY_BREAKS))

def score_distance_main(value) -> float:
    return _score(value, AMENITY_W, lambda v: _lookup_by_threshold(float(v), AMENITY_BREAKS))

def score_alley_level(value) -> float:
    return _score(value, AMENITY_W, lambda v: _lookup_by_threshold(float(v), AMENITY_BREAKS))

def score_alley_type(value: Optional[str]) -> float:
    if value is None:
        return 0.0
    k = ALLEY_TYPE_TABLE.get(value)
    if k is None:
        return 0
    return k * ALLEY_TYPE_W

def score_alley_quality(value: Optional[str]) -> float:
    if value is None:
        return 0.0
    k = ALLEY_QUALITY_TABLE.get(value)
    if k is None:
        return 0
    return k * ALLEY_QUALITY_W

def score_sidewalk(value) -> float:
    return _score(value, SIDEWALK_W, lambda v: _lookup_by_threshold(float(v), SIDEWALK_BREAKS))

def score_area(value) -> float:
    return _score(value, LAND_AREA_W, lambda v: _lookup_by_threshold(float(v), LAND_AREA_BREAKS))

def score_shape(value: Optional[str]) -> float:
    if value is None:
        return 0.0
    k = SHAPE_TABLE.get(value)
    if k is None:
        return 0
    return k * SHAPE_W

def score_rear_shape(value: Optional[str]) -> float:
    if value is None:
        return 0.0
    k = REAR_SHAPE_TABLE.get(value)
    if k is None:
        return 0
    return k * REAR_SHAPE_W

def score_frontage_width(value) -> float:
    return _score(value, FRONTAGE_WIDTH_W, lambda v: _lookup_by_threshold(float(v), FRONTAGE_WIDTH_BREAKS))

def score_frontage_count(value) -> float:
    return _score(value, FRONTAGE_COUNT_W, lambda v: _lookup_by_threshold(float(v), FRONTAGE_COUNT_BREAKS))

def score_floor_area(value) -> float:
    return _score(value, FLOOR_AREA_W, lambda v: _lookup_by_threshold(float(v), FLOOR_AREA_BREAKS))

def score_building_grade(value: Optional[str]) -> float:
    if value is None:
        return 0.0
    k = BUILDING_GRADE_TABLE.get(value)
    if k is None:
        return 0
    return k * BUILDING_GRADE_W

def score_school(value) -> float:
    return _score(value, SCHOOL_W, lambda v: _lookup_by_threshold(float(v), SCHOOL_BREAKS))

def score_hospital(value) -> float:
    return _score(value, HOSPITAL_W, lambda v: _lookup_by_threshold(float(v), HOSPITAL_BREAKS))

def score_mall(value) -> float:
    return _score(value, MALL_W, lambda v: _lookup_by_threshold(float(v), MALL_BREAKS))

def score_supermarket(value) -> float:
    return _score(value, SUPERMARKET_W, lambda v: _lookup_by_threshold(float(v), SUPERMARKET_BREAKS))

def score_metro(value) -> float:
    return _score(value, METRO_W, lambda v: _lookup_by_threshold(float(v), METRO_BREAKS))

def score_park(value) -> float:
    return _score(value, PARK_W, lambda v: _lookup_by_threshold(float(v), PARK_BREAKS))

def score_cbd_dist(value) -> float:
    return _score(value, CBD_DIST_W, lambda v: _lookup_by_threshold(float(v), CBD_DIST_BREAKS))

def score_admin_center(value) -> float:
    return _score(value, ADMIN_CENTER_W, lambda v: _lookup_by_threshold(float(v), ADMIN_CENTER_BREAKS))

def score_market(value) -> float:
    return _score(value, MARKET_W, lambda v: _lookup_by_threshold(float(v), MARKET_BREAKS))

def score_view(value: Optional[str]) -> float:
    if value is None:
        return 0.0
    k = VIEW_TABLE.get(value)
    if k is None:
        return 0
    return k * VIEW_W

def score_landfill(value) -> float:
    return _score(value, LANDFILL_W, lambda v: _lookup_by_threshold(float(v), LANDFILL_BREAKS))

def score_wastewater(value) -> float:
    return _score(value, WASTEWATER_W, lambda v: _lookup_by_threshold(float(v), WASTEWATER_BREAKS))

def score_airport(value) -> float:
    return _score(value, AIRPORT_W, lambda v: _lookup_by_threshold(float(v), AIRPORT_BREAKS))

def score_railway(value) -> float:
    return _score(value, RAILWAY_W, lambda v: _lookup_by_threshold(float(v), RAILWAY_BREAKS))

def score_cemetery(value) -> float:
    return _score(value, CEMETERY_W, lambda v: _lookup_by_threshold(float(v), CEMETERY_BREAKS))

def score_funeral_home(value) -> float:
    return _score(value, FUNERAL_HOME_W, lambda v: _lookup_by_threshold(float(v), FUNERAL_HOME_BREAKS))

def score_temple(value) -> float:
    return _score(value, TEMPLE_W, lambda v: _lookup_by_threshold(float(v), TEMPLE_BREAKS))

# ===========================================================================
# WEIGHTS CỦA TỪNG FEATURE (để tính max_possible)
# ===========================================================================

FEATURE_WEIGHTS: dict[str, float] = {
    "road_type":       ROAD_TYPE_W,
    "road_width":      ROAD_WIDTH_W,
    "poi_density":     POI_DENSITY_W,
    "amenity":         AMENITY_W,
    "sidewalk":        SIDEWALK_W, # 5
    "alley_cap":       ALLEY_CAP_W,
    "distance_main":   DISTANCE_MAIN_W,
    "alley_level":     ALLEY_LEVEL_W,
    "alley_type":      ALLEY_TYPE_W,
    "alley_quality":   ALLEY_QUALITY_W, # 5
    "area":            LAND_AREA_W,
    "shape":           SHAPE_W,
    #"ratio":           RATIO_W,
    "rear_shape":      REAR_SHAPE_W,
    "frontage_width":  FRONTAGE_WIDTH_W,
    "frontage_count":  FRONTAGE_COUNT_W,
    "floor_area":      FLOOR_AREA_W,
    "building_grade":  BUILDING_GRADE_W, # 8
    "school":          SCHOOL_W,
    "hospital":        HOSPITAL_W,
    "mall":            MALL_W,
    "supermarket":     SUPERMARKET_W,
    "metro":           METRO_W,
    "park":            PARK_W,
    "cbd_dist":        CBD_DIST_W,
    "admin_center":    ADMIN_CENTER_W,
    "market":          MARKET_W,
    "view":            VIEW_W, # 10
    "landfill":        LANDFILL_W,
    "wastewater":      WASTEWATER_W,
    "airport":         AIRPORT_W,
    "railway":         RAILWAY_W,
    "cemetery":        CEMETERY_W,
    "funeral_home":    FUNERAL_HOME_W,
    "temple":          TEMPLE_W, # 7
}

SCORE_FUNCTIONS = {
    "road_type":       score_road_type,
    "road_width":      score_road_width,
    "poi_density":     score_poi_density,
    "amenity":         score_amenity,
    "sidewalk":        score_sidewalk,
    "alley_cap":       score_alley_cap,
    "distance_main":   score_distance_main,
    "alley_level":     score_alley_level,
    "alley_type":      score_alley_type,
    "alley_quality":   score_alley_quality, # 5
    "area":            score_area,
    "shape":           score_shape,
    #"ratio":           score_ratio,
    "rear_shape":      score_rear_shape,
    "frontage_width":  score_frontage_width,
    "frontage_count":  score_frontage_count,
    "floor_area":      score_floor_area,
    "building_grade":  score_building_grade,
    "school":          score_school,
    "hospital":        score_hospital,
    "mall":            score_mall,
    "supermarket":     score_supermarket,
    "metro":           score_metro,
    "park":            score_park,
    "cbd_dist":        score_cbd_dist,
    "admin_center":    score_admin_center,
    "market":          score_market,
    "view":            score_view,
    "landfill":        score_landfill,
    "wastewater":      score_wastewater,
    "airport":         score_airport,
    "railway":         score_railway,
    "cemetery":        score_cemetery,
    "funeral_home":    score_funeral_home,
    "temple":          score_temple,
}

# ---------------------------------------------------------------------------
# Hàm tổng hợp
# ---------------------------------------------------------------------------

def calculate_f_score(house: dict) -> dict:
    """
    Tính tổng điểm thương mại cho một ngôi nhà.

    Parameters
    ----------
    house : dict
        JSON với các key:
          - road_type    : str  ("CBD" | "Trục chính" | "Khu vực" | "Nội khu" | "Đường nhỏ")
          - road_width   : float (mét)
          - poi_density  : int   (số POI)
          - amenity      : int   (số nhóm tiện ích)
          - sidewalk     : float (mét)

    Returns
    -------
    dict
        {
            "total_score"  : float,   # tổng điểm (tối đa 0.80)
            "normalized"   : float,   # điểm chuẩn hóa về [0, 1]
            "breakdown"    : dict     # chi tiết từng feature
        }
    """
    breakdown: dict[str, float] = {}
    max_possible = 0.0

    for feature, fn in SCORE_FUNCTIONS.items():
        value = house.get(feature)   # None nếu thiếu
        weighted = fn(value)
        breakdown[feature] = round(weighted, 4)
        #max_possible += FEATURE_WEIGHTS[feature]   # luôn cộng W, kể cả khi value=None (K=0)

    total = sum(breakdown.values())
    return total
    # return {
    #     "total_score": round(total, 4),
    #     #"normalized":  round(total / max_possible, 4),
    #     "breakdown":   {k: round(v, 4) for k, v in breakdown.items()},
    # }

def calculate_P_by_f_score(data: dict) -> dict:
    target = flatten(data["target_asset"])
    f_target = calculate_f_score(target)

    results = []

    for asset in data["comparable_assets"]:
        comp = flatten(asset)
        f_comp = calculate_f_score(comp)

        # tránh chia 0
        if f_comp == 0:
            p = None
        else:
            p = comp.get("price") * f_target * target.get("area") / (f_comp * comp.get("area"))

        results.append({
            "asset_id": comp.get("asset_id"),
            "price": comp.get("price"),
            "f_score": round(f_comp, 4),
            "P_tsmt": round(p) if p else None,
            #"k*W": f_target['breakdown']
        })

    return {
        "target_asset": {
            "asset_id": target.get("asset_id"),
            "f_score": round(f_target, 4),
            #"k*W": f_comp['breakdown']
        },

        "comparable_assets": results
    }

# ---------------------------------------------------------------------------
# flatten json -> dict
# ---------------------------------------------------------------------------

def flatten(asset: dict) -> dict:
    """
    Flatten asset:
    - giữ các field thường
    - bung các dict con (nearby, features, ...)
    - bỏ dict lồng sâu hơn
    """
    result = {}

    for k, v in asset.items():
        # dict con -> bung ra
        if isinstance(v, dict):
            for sub_k, sub_v in v.items():
                # chỉ lấy primitive
                if not isinstance(sub_v, dict):
                    result[sub_k] = sub_v
        else:
            result[k] = v

    return result

# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

# if __name__ == "__main__":
#     import json

#     sample = {
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
#         "note": "Hẻm ô tô - nhà mới full nội thất"
#         }
#     ]
#     }
#     target = flatten(sample["target_asset"])
#     result = calculate_P_by_f_score(sample)
#     print("Input:", json.dumps(sample, ensure_ascii=False, indent=2))
#     print("\nOutput:")
#     #print(result)
#     print(json.dumps(result, ensure_ascii=False, indent=2))

