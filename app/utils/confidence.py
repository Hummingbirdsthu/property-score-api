"""
Tính độ tin cậy (Confidence Score) cho kết quả định giá AVM.
Đầu vào: JSON schema bên ngoài sau khi chạy calculate_P_by_f_score.
"""

from datetime import datetime, date

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
    "cong_chung":   100,
    "registry":     100,
    "core_banking":  95,
    "third_party":   90,
    "khung_gia":     90,
    "listing":       85,
    "user_input":    80,
}

def score_nguon(source: str) -> int:
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


def calc_spread(p_list: list) -> float:
    if len(p_list) < 2:
        return 0.0
    pmax, pmin, pavg = max(p_list), min(p_list), sum(p_list) / len(p_list)
    return (pmax - pmin) / pavg * 100 if pavg else 0.0


# ---------------------------------------------------------------------------
# 6. Overall Confidence Score
# ---------------------------------------------------------------------------

WEIGHTS = {
    "so_luong":    0.15,
    "khoang_cach": 0.25,
    "thoi_gian":   0.25,
    "nguon":       0.20,
    "bien_gia":    0.15,
}

def overall_confidence(scores: dict) -> float:
    return sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)


# ---------------------------------------------------------------------------
# 7. Confidence Grade
# ---------------------------------------------------------------------------

def grade(cs: float) -> tuple:
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

def warnings(n_tsss, avg_distance_m, avg_days, spread_pct, source_score) -> list:
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


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def days_since(transaction_date) -> float:
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
    Đầu vào : JSON schema bên ngoài sau khi chạy calculate_P_by_f_score.
    Trả về  : data gốc được bổ sung key "confidence".

    Các field đọc từ schema bên ngoài:
        - Comparable_Assets[i].Comparable_Distances[0].DistanceM
        - Comparable_Assets[i].Comparable_Transaction.Transaction_Date
        - Comparable_Assets[i].Comparable_Transaction.Transaction_Price
        - Comparable_Assets[i].Comparable_Property_Detail.Land_Area
        - Comparable_Assets[i].data_source   (tuỳ chọn)
    """
    comps = data.get("Comparable_Assets", [])
    n = len(comps)

    # Lấy DistanceM từ Comparable_Distances[0]
    comps_with_dist = [
        c for c in comps
        if c.get("Comparable_Distances") and
           c["Comparable_Distances"][0].get("DistanceM") is not None
    ]

    # 1. Số lượng
    k_so_luong = score_so_luong(n)

    # 2. Khoảng cách trung bình
    avg_dist = sum(c["Comparable_Distances"][0]["DistanceM"] for c in comps_with_dist) / len(comps_with_dist)
    k_khoang_cach = score_khoang_cach(avg_dist)

    # 3. Thời gian trung bình — Transaction_Date trong Comparable_Transaction
    ages = []
    for c in (comps_with_dist if comps_with_dist else comps):
        td = c.get("Comparable_Transaction", {}).get("Transaction_Date")
        if td:
            ages.append(days_since(td))
    avg_days = sum(ages) / len(ages) if ages else 0.0
    k_thoi_gian = score_thoi_gian(avg_days)

    # 4. Nguồn dữ liệu
    source_scores = []
    for c in comps:
        src = c.get("data_source")
        if src:
            source_scores.append(score_nguon(src))
    k_nguon = round(sum(source_scores) / len(source_scores)) if source_scores else 85

    # 5. Biên giá — đơn giá = Transaction_Price / Land_Area
    p_list = []
    for c in comps:
        price = c.get("Comparable_Transaction", {}).get("Transaction_Price")
        area  = c.get("Comparable_Property_Detail", {}).get("Land_Area")
        if price and area:
            p_list.append(price / area)
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

    return {
        "PropertyId":      data.get("PropertyId"),
        "overall_score": round(cs, 2),
        "grade":         cs_grade,
        "meaning":       cs_meaning,
        "component_scores": {
            "so_luong_tsss": {"score": k_so_luong,    "weight": "15%", "n": n},
            "khoang_cach":   {"score": k_khoang_cach, "weight": "25%", "avg_distance_m": round(avg_dist, 1)},
            "thoi_gian":     {"score": k_thoi_gian,   "weight": "25%", "avg_days": round(avg_days, 1)},
            "nguon_du_lieu": {"score": k_nguon,        "weight": "20%"},
            "bien_gia":      {"score": k_bien_gia,     "weight": "15%", "spread_pct": round(spread, 2)},
        },
        "warnings": warns,
    }
    


# if __name__ == "__main__":
#     import json

#     sample = {
#     "PropertyId": "TSMT",
#     "PropertyType": "Nha_o",
#     #"CollateralFlag": false,
#     "OwnershipPercentage": 0,
#     "DisputeFlag": "Khong_tranh_chap",
#     #"MortgageFlag": false,
#     "LandAreaTotal": 50,
#     "LandUsePurpose": "ODT___t______th_",
#     "RoadAccessType": "M_t_ti_n",
#     "FrontageWidth": 50,
#     "RoadWidth": 10,
#     #"AlleyFlag": false,
#     "Version": 0,
#     "Tax_Obligations": "___n_p",
#     "Planning": "Kh_ng_quy_ho_ch",
#     "frontage_count": 1,
#     "distance_to_main_road": 10,
#     "Construction_Area": 50,
#     #"Property_On_land": false,
#     "structure_type": "B__t_ng_c_t_th_p",

#     "PropertyLocation": {
#         "HouseNumber": "",
#         "Street": "Đường Nguyễn Thượng Hiền",
#         "Ward": "Phường 6",
#         "District": "Quận Bình Thạnh",
#         "Province": "Hồ Chí Minh",
#         "Latitude": 10.80560109,
#         "Longitude": 106.68607077,
#         "LocationScore": 0
#     },

#     "Comparable_Assets": [
#         {
#         "Comparable_id": "117.49254466",
#         "property_type": "Nhà mặt phố",
#         "address": "Đường Nguyễn Thượng Hiền, Phường 6, Quận Bình Thạnh, Hồ Chí Minh",
#         "ward": "Phường 6",
#         "district": "Quận Bình Thạnh",
#         "province": "Hồ Chí Minh",
#         "Latitude": 10.80833966,
#         "longtitude": 106.684205,
#         "Note": "Bán nhanh trong tháng chỉ 16tỷ9 ngay mặt tiền doanh thu 90tr/tháng",

#         "Comparable_Property_Detail": {
#             "Land_Area": 900,
#             "Building_Area": 0,
#             "Frontage": 0,
#             "Road_width": 0,
#             "Floor_Count": 30,
#             "Construction_year": 0,
#             "Legal_status": "sổ đỏ/sổ hồng"
#         },

#         "Comparable_Transaction": {
#             "Transaction_Price": 16900000000000000,
#             "Listing_Price": 0,
#             "Price_Per_m2": 0,
#             "Transaction_Date": "2026-05-04T17:00:00.000Z",
#             "Distance_To_Subject": 0
#         },

#         "Advantages": {
#             "Nearest_School": 191,
#             "Nearest_Hospital": 462.4,
#             "Nearest_Market": 144.8,
#             "Nearest_cemetery": 730.2,
#             "Nearest_Airport": 3297.1,
#             "Nearest_Railway": 839.8,
#             "Nearest_landfill": 4140.6,
#             "Nearest_Pagoda": 158.9
#         },

#         "Comparable_Distances": [
#             {
#             "DistanceM": 365.23009145
#             }
#         ]
#         },

#         {
#         "Comparable_id": "117.49252595",
#         "property_type": "Nhà mặt phố",
#         "address": "Đường Nguyễn Thượng Hiền, Phường 5, Quận Phú Nhuận, Hồ Chí Minh",
#         "ward": "Phường 5",
#         "district": "Quận Phú Nhuận",
#         "province": "Hồ Chí Minh",
#         "Latitude": 10.80819335,
#         "longtitude": 106.6843326,
#         "Note": "Thu nhập 400 triệu - 105 tỷ! Bán tòa nhà 1946m2 Nguyễn Thượng Hiền, Bình Thạnh - Hầm 9 Tầng",

#         "Comparable_Property_Detail": {
#             "Land_Area": 28517,
#             "Building_Area": 0,
#             "Frontage": 124,
#             "Road_width": 0,
#             "Floor_Count": 80,
#             "Construction_year": 0,
#             "Legal_status": "sổ đỏ/sổ hồng"
#         },

#         "Comparable_Transaction": {
#             "Transaction_Price": 1050000000000,
#             "Listing_Price": 0,
#             "Price_Per_m2": 0,
#             "Transaction_Date": "2026-05-08T17:00:00.000Z",
#             "Distance_To_Subject": 0
#         },

#         "Advantages": {
#             "Nearest_School": 172.2,
#             "Nearest_Hospital": 441,
#             "Nearest_Market": 153.6,
#             "Nearest_cemetery": 751.6,
#             "Nearest_Airport": 3315.7,
#             "Nearest_Railway": 855.3,
#             "Nearest_landfill": 4131.2,
#             "Nearest_Pagoda": 150.8
#         },

#         "Comparable_Distances": [
#             {
#             "DistanceM": 344.02104631
#             }
#         ]
#         }
#     ],

#     "Legal_Certificate": {
#         "Certificate_Serial": "po09839582",
#         "Issue_Date": "2026-04-30T17:00:00.000Z",
#         "Certificate_type": "So_do"
#     },

#     "Advantages": {
#         "Nearest_School": 43.7,
#         "Nearest_Hospital": 100.4,
#         "Nearest_Market": 380.8,
#         "Nearest_Airport": 3597.1,
#         "Nearest_Railway": 1153.2,
#         "Nearest_landfill": 4033.1,
#         "Nearest_Pagoda": 212.3
#     }
#     }
#     #target = flatten_external_target(sample)
#     result = calculate_confidence(sample)
#     #print("Input:", json.dumps(sample, ensure_ascii=False, indent=2))
#     print("\nOutput:")
#     #print(result)
#     print(json.dumps(result, ensure_ascii=False, indent=2))

