from sqlalchemy import Column, Integer, String, BigInteger, Float, Text
from geoalchemy2 import Geography
from app.core.database import Base


class HousePostGIS(Base):
    __tablename__ = "house_postgis"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True)
    gia_khoang = Column(BigInteger)
    dien_tich = Column(Float)
    so_phong_ngu = Column(Float)
    so_phong_tam = Column(Float)
    huong_nha = Column(Text)
    huong_ban_cong = Column(Text)
    phap_ly = Column(Text)
    noi_that = Column(Text)
    ngay_dang = Column(Text)
    ten_du_an = Column(Text)
    longitude = Column(Float)
    latitude = Column(Float)
    location = Column(Geography("POINT", srid=4326))
    chu_dau_tu = Column(Text)
    dia_chi = Column(Text)
    loai_nha = Column(Text)
    link = Column(Text)
    so_tang = Column(Integer)
    mat_tien = Column(Float)
    duong_vao = Column(Float)
    title = Column(Text)
    thanh_pho = Column(Text)
    quan_huyen = Column(Text)
    phuong_xa = Column(Text)