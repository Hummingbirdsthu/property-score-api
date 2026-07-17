import math
import difflib
from datetime import date
from typing import Dict, List, Tuple, Optional, Any
from sqlalchemy.orm import Session, joinedload
from app.models.lookup import LookupFeature, LookupValue
from app.schemas.comparative_property import ComparativeProperty, Location
from app.utils.helper import cosine_similarity, format_string
from app.models.comparative_property import HousePostGIS


class ComparativePropertyService:
    """
    Bước 1 - LỌC BÁN KÍNH ĐỊA LÝ:
        Chỉ giữ lại các TSSS nằm trong bán kính `ban_kinh_m` (mét) quanh TSMT
        (tính bằng khoảng cách haversine giữa 2 tọa độ). TSSS ngoài bán kính bị loại
        ngay, không tính similarity.

    Bước 2 - COSINE SIMILARITY TRÊN VECTOR ĐẶC TRƯNG:
        lọc, xây vector đặc trưng gồm:
          - Số: land_area, Construction_Area, RoadWidth/frontage_width,
                distance_to_main_road, NumberOfFloors, tuổi công trình
                (min-max normalize trong phạm vi TSMT + các TSSS đã lọc)
          - Phân loại (one-hot): PropertyType, LandUsePurpose, RoadAccessType,
                structure_type, AlleyFlag
        tính cosine similarity giữa vector TSMT và từng vector TSSS, sắp xếp
        giảm dần, lấy tối đa `so_luong_toi_da` kết quả (ít hơn nếu không đủ ứng viên).

    Cách dùng:
        from tim_tsss import tim_tsss
        ket_qua = tim_tsss(tsmt, danh_sach_ung_vien, ban_kinh_m=2000, so_luong_toi_da=3)
    """

    _FEATURES_SO = [
        "land_area",
        "Construction_Area",
        "_do_rong_duong",  # RoadWidth hoặc frontage_width, tính riêng bên dưới
        "distance_to_main_road",
        "_so_tang",  # BuildingInfo.NumberOfFloors
        "_tuoi_cong_trinh",  # tính từ BuildingInfo.ConstructionYear
    ]

    _FEATURES_PHAN_LOAI = [
        "PropertyType",
        "LandUsePurpose",
        "RoadAccessType",
        "structure_type",
    ]

    PROPERTY_LOCATION_LATITUDE = "PropertyLocation.Latitude"
    PROPERTY_LOCATION_LONGTITUDE = "PropertyLocation.Longitude"
    PROPERTY_LOCATION_HOUSENUMBER = "PropertyLocation.HouseNumber"
    PROPERTY_LOCATION_STREET = "PropertyLocation.Street"
    PROPERTY_LOCATION_WARD = "PropertyLocation.Ward"
    PROPERTY_LOCATION_PROVINCE = "PropertyLocation.Province"
    PROPERTY_LOCATION_CONSTRUCTION_YEAR = "BuildingInfo.ConstructionYear"

    LATITUDE = "Latitude"
    LONGTITUDE = "longtitude"
    ALLEY_FLAG = "AlleyFlag"

    def __init__(self, db: Session):
        self.prospects = self._get_prospects(db)
        self.min_max = {}
        self.distance_maps = {}
        self.cat = {}
        self.vec_one_hot = []
        self.properties = []

    def _get(self, d: dict, path: str, default=None):
        cur = d
        for part in path.split("."):
            if not isinstance(cur, dict) or part not in cur or cur[part] is None:
                return default
            cur = cur[part]
        return cur

    def _get_address(self, ts):
        parts = [
            self._get(ts, self.PROPERTY_LOCATION_HOUSENUMBER),
            self._get(ts, self.PROPERTY_LOCATION_STREET),
            self._get(ts, self.PROPERTY_LOCATION_WARD),
            self._get(ts, self.PROPERTY_LOCATION_PROVINCE),
        ]
        return ", ".join(p for p in parts if p)

    def _map(self, housePostGIS: HousePostGIS):
        # TODO: Missing infomation for comparative assets in house_postgis
        return {
            "Comparable_id": housePostGIS.id,
            "property_type": housePostGIS.loai_nha,
            "address": housePostGIS.dia_chi,
            "ward": housePostGIS.phuong_xa,
            "district": housePostGIS.quan_huyen,
            "province": housePostGIS.thanh_pho,
            "Latitude": housePostGIS.latitude,
            "longtitude": housePostGIS.longitude,
            "Note": None,
            "Comparable_Property_Detail": {
                "Land_Area": housePostGIS.dien_tich or 0,
                "Building_Area": 0,
                "Frontage": housePostGIS.mat_tien or 0,
                "Road_width": 0,
                "Floor_Count": housePostGIS.so_tang or 0,
                "Construction_year": 0,
                "Legal_status": housePostGIS.phap_ly,
            },
            "Comparable_Transaction": {
                "Transaction_Price": housePostGIS.gia_khoang or 0,
                "Listing_Price": 0,
                "Price_Per_m2": 0,
                "Transaction_Date": None,
                "Distance_To_Subject": 0,
            },
            "Advantages": {
                "Nearest_School": 0,
                "Nearest_Hospital": 0,
                "Nearest_Market": 0,
                "Nearest_Airport": 0,
                "Nearest_Railway": 0,
                "Nearest_landfill": 0,
                "Nearest_mall": 0,
                "Nearest_Pagoda": 0,
            },
            "Comparable_Distances": [{"DistanceM": 0}],
        }

    def _get_prospects(self, db: Session):
        rows = db.query(HousePostGIS).all()
        result = [self._map(r) for r in rows]
        return result

    def _get_vec_features(self, prototype: dict) -> list[float]:
        vec = []
        for feat in self._FEATURES_SO:
            mm = self.min_max[feat]
            v = prototype[feat]
            if mm is None or v is None or mm[1] == mm[0]:
                vec.append(0.5)  # trung tính khi thiếu dữ liệu hoặc không có phương sai
            else:
                vec.append((v - mm[0]) / (mm[1] - mm[0]))
        return vec

    def _one_hot(self, property: dict):
        vec = []
        for feat in self._FEATURES_PHAN_LOAI:
            v = format_string(self._get(property, feat))
            for cat in cat[feat]:
                vec.append(1.0 if v == cat else 0.0)
        af = self._get(property, self.ALLEY_FLAG)
        vec.append(0.5 if af is None else (1.0 if af else 0.0))
        return vec

    def _filter_by_radius(self, property_target: dict, radius: float):
        """
        Args:


        Returns:
            Trả về list (tsss, khoang_cach_m) — chỉ những cái nằm trong bán kính.
            Nếu thiếu tọa độ ở 1 trong 2 bên, fallback so khớp địa chỉ text (ratio >= 0.6)
            và khoang_cach_m trả về None (không xác định được bằng số mét).
        """
        location1 = Location(
            latitude=self._get(property_target, self.PROPERTY_LOCATION_LATITUDE),
            longtitude=self._get(property_target, self.PROPERTY_LOCATION_LONGTITUDE),
        )

        result = []
        for prop in self.prospects:
            location2 = Location(
                latitude=self._get(property_target, self.PROPERTY_LOCATION_LATITUDE)
                or self._get(property_target, self.LATITUDE),
                longtitude=self._get(property_target, self.PROPERTY_LOCATION_LONGTITUDE)
                or self._get(property_target, self.LONGTITUDE),
            )

            if not (location1.valid() and location2.valid):
                d = location1.calc_distance(location2)
                if d <= radius:
                    result.append((property_target, d))
                continue

            dc1, dc2 = self._get_address(property_target), self._get_address(prop)
            if (
                dc1
                and dc2
                and difflib.SequenceMatcher(None, dc1.lower(), dc2.lower()).ratio()
                >= 0.6
            ):
                result.append((prop, None))

        return result

    def _get_prototype(self, property_target) -> dict:
        construction_year = self._get(
            property_target, self.PROPERTY_LOCATION_CONSTRUCTION_YEAR
        )

        return {
            "land_area": self._get(property_target, "land_area"),
            "Construction_Area": self._get(property_target, "Construction_Area"),
            "_do_rong_duong": self._get(property_target, "RoadWidth")
            or self._get(property_target, "frontage_width"),
            "distance_to_main_road": self._get(
                property_target, "distance_to_main_road"
            ),
            "_so_tang": self._get(property_target, "BuildingInfo.NumberOfFloors"),
            "_tuoi_cong_trinh": (
                date.today().year - construction_year if construction_year else None
            ),
        }

    def _build_vector(
        self, property_target: dict
    ) -> tuple[list[float], list[list[float]]]:
        """
        Xây vector đặc trưng (min-max normalize theo phạm vi TSMT + ứng viên) cho TSMT
        và từng ứng viên, gồm khối số (normalize [0,1]) nối với khối one-hot phân loại.
        """
        mixed_array = [property_target] + self.prospects
        prototypes = [self._get_prototype(p) for p in mixed_array]

        for feat in self._FEATURES_SO:
            values = [p[feat] for p in prototypes if p[feat] is not None]
            self.min_max[feat] = (min(values), max(values)) if values else None

        for feat in self._FEATURES_PHAN_LOAI:
            gia_tri = {format_string(self._get(t, feat)) for t in mixed_array}
            gia_tri.discard("")
            self.cat[feat] = sorted(gia_tri)

        vec_tsmt = self._get_vec_features(prototypes[0]) + self._one_hot(
            property_target
        )
        vec_ung_vien = [
            self._get_vec_features(prototypes[i + 1]) + self._one_hot(t)
            for i, t in enumerate(property_target)
        ]
        return vec_tsmt, vec_ung_vien

    def find(
        self, property_target: dict, radius: float = 2000, max_length: int = 3
    ) -> list[ComparativeProperty]:
        """
        Args:
            tsmt: dict JSON tài sản mục tiêu.
            danh_sach_ung_vien: list dict TSSS tiềm năng.
            ban_kinh_m: bán kính lọc quanh TSMT, tính bằng mét.
            so_luong_toi_da: số TSSS tối đa muốn lấy. Nếu sau khi lọc bán kính còn ít
                            ứng viên hơn con số này, trả về đúng số ít hơn đó (có thể là 0).

        Returns:
            list[KetQuaTSSS] sắp xếp giảm dần theo do_tuong_dong, độ dài <= so_luong_toi_da.
        """
        in_range_prospects = self._filter_by_radius(property_target, radius)
        if not in_range_prospects:
            return []

        for prop, dis in in_range_prospects:
            self.properties.append(prop)
            self.distance_maps[id(prop)] = dis
            # self.distance_maps.update({id(prop), dis})

        vec_property_target, vec_prospect = self._build_vector(property_target)

        result = []
        for ts, vec in zip(self.properties, vec_prospect):
            sim = cosine_similarity(vec_property_target, vec)
            result.append(
                ComparativeProperty(
                    tai_san=ts,
                    khoang_cach_m=self._calculate_distance[id(ts)],
                    do_tuong_dong=round(sim, 4),
                )
            )

        result.sort(key=lambda x: x.do_tuong_dong, reverse=True)
        print(f"find: {result}")
        return result[:max_length]
