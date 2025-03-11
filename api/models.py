# Dans api/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()

class Poteau(Base):
    __tablename__ = 'poteaux'

    id = Column(Integer, primary_key=True)
    FID = Column(Integer)
    OBJECTID = Column(Integer)
    EXPL_ID = Column(Integer)
    POSTHTABT_ = Column(String)
    SUPPORT_ID = Column(String)
    SUPPORT_PL = Column(String)
    SUPPORT_NU = Column(String)
    SUPPORT__1 = Column(String)
    CAR_PHYSIQ = Column(String)
    SUPPORT_X = Column(Float)
    SUPPORT_Y = Column(Float)
    SUPPORT_SI = Column(String)
    QUARTIER_C = Column(String)
    SUPPORT_CH = Column(String)
    SUPPORT_DI = Column(String)
    STATUT_COD = Column(String)
    SUPPORT_DT = Column(String)
    SUPPORT__2 = Column(String)
    MODE_FINAN = Column(String)
    PROJET_ID = Column(String)
    USER_ID = Column(String)
    DT_CRE = Column(String)
    DT_MAJ = Column(String)
    PROJET_ID_ = Column(String)
    VILLE = Column(String)
    EXPLOIT = Column(String)
    geom = Column(Geometry('POINT', srid=4326))
