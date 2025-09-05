from geoalchemy2 import Geometry
from sqlalchemy import Column, Float, String
from sqlalchemy.orm import relationship

from flood_monitoring.core.database import Base


class Station(Base):

    __tablename__ = "stations"

    id_stacji = Column(String, primary_key=True)
    stacja = Column(String, nullable=False)
    rzeka = Column(String)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    geom = Column(Geometry("POINT", srid=4326), nullable=False)
    wojewodztwo = Column(String, nullable=False)

    stan_measurements = relationship("StanMeasurement", back_populates="station")
    przeplyw_measurements = relationship(
        "PrzeplywMeasurement", back_populates="station"
    )

    def __repr__(self):
        return f"<Station(id_stacji='{self.id_stacji}', stacja='{self.stacja}')>"
