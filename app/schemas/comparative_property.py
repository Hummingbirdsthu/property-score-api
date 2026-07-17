import math
from dataclasses import dataclass
from typing import Optional


class ComparativeProperty:
    tai_san: dict
    khoang_cach_m: Optional[float]
    do_tuong_dong: float


@dataclass
class Location:
    latitude: float
    longtitude: float

    def valid(self):
        return self.latitude != None and self.longtitude != None
    
    def calc_distance(self, other: "Location") -> float:
        R = 6371000.0
        p1, p2 = math.radians(self.latitude), math.radians(other.latitude)
        dphi = math.radians(other.latitude - self.latitude)
        dlmb = math.radians(other.longtitude - self.longtitude)
        a = (
            math.sin(dphi / 2) ** 2
            + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
        )
        return 2 * R * math.asin(math.sqrt(a))
