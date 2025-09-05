from sqlalchemy import Column, DateTime, Float, ForeignKey, String, UniqueConstraint, Index
from sqlalchemy.orm import relationship

from flood_monitoring.core.database import Base


class StanMeasurement(Base):

    __tablename__ = "stan_measurements"

    id = Column(
        String, primary_key=True
    )
    station_id = Column(String, ForeignKey("stations.id_stacji"), nullable=False)
    stan_wody_data_pomiaru = Column(DateTime, nullable=False)
    stan_wody = Column(Float, nullable=False)

    station = relationship("Station", back_populates="stan_measurements")

    __table_args__ = (
        UniqueConstraint("station_id", "stan_wody_data_pomiaru", name="uix_station_stan_time"),
        Index("ix_stan_station_id", "station_id"),
        Index("ix_stan_data_pomiaru", "stan_wody_data_pomiaru"),
        Index("ix_stan_station_date", "station_id", "stan_wody_data_pomiaru"),
    )

    def __repr__(self):
        return f"<StanMeasurement(station_id='{self.station_id}', stan_wody_data_pomiaru='{self.stan_wody_data_pomiaru}')>"


class PrzeplywMeasurement(Base):

    __tablename__ = "przeplyw_measurements"

    id = Column(
        String, primary_key=True
    )
    station_id = Column(String, ForeignKey("stations.id_stacji"), nullable=False)
    przeplyw_data = Column(DateTime, nullable=False)
    przelyw = Column(Float, nullable=False)

    station = relationship("Station", back_populates="przeplyw_measurements")

    __table_args__ = (
        UniqueConstraint(
            "station_id", "przeplyw_data", name="uix_station_przeplyw_time"
        ),
        Index("ix_przeplyw_station_id", "station_id"),
        Index("ix_przeplyw_data", "przeplyw_data"),
        Index("ix_przeplyw_station_date", "station_id", "przeplyw_data"),
    )

    def __repr__(self):
        return f"<PrzeplywMeasurement(station_id='{self.station_id}', przeplyw_data='{self.przeplyw_data}')>"
