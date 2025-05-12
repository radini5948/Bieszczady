"""
Model dla stacji pomiarowych
"""
from geoalchemy2 import Geometry
from sqlalchemy import Column, Float, String
from sqlalchemy.orm import relationship

from flood_monitoring.core.database import Base


class Station(Base):
    """Model stacji pomiarowej"""

    __tablename__ = "stations"

    kod_stacji = Column(String, primary_key=True)
    nazwa_stacji = Column(String, nullable=False)
    rzeka = Column(String)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    geom = Column(Geometry("POINT", srid=4326), nullable=False)

    # Relacje do pomiarów
    stan_measurements = relationship("StanMeasurement", back_populates="station")
    przeplyw_measurements = relationship(
        "PrzeplywMeasurement", back_populates="station"
    )

    def __repr__(self):
        return f"<Station(kod_stacji='{self.kod_stacji}', nazwa_stacji='{self.nazwa_stacji}')>"
