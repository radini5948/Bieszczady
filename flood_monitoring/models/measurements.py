"""
Modele dla pomiarów stanu wody i przepływu
"""
from sqlalchemy import Column, DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from flood_monitoring.core.database import Base


class StanMeasurement(Base):
    """Model pomiaru stanu wody"""

    __tablename__ = "stan_measurements"

    id = Column(
        String, primary_key=True
    )  # Możemy użyć kombinacji kod_stacji + timestamp jako id
    station_id = Column(String, ForeignKey("stations.id_stacji"), nullable=False)
    stan_wody_data_pomiaru = Column(DateTime, nullable=False)
    stan_wody = Column(Float, nullable=False)

    # Relacja do stacji
    station = relationship("Station", back_populates="stan_measurements")

    # Unikalny constraint na kombinację stacji i czasu
    __table_args__ = (
        UniqueConstraint("station_id", "stan_wody_data_pomiaru", name="uix_station_stan_time"),
    )

    def __repr__(self):
        return f"<StanMeasurement(station_id='{self.station_id}', stan_wody_data_pomiaru='{self.stan_wody_data_pomiaru}')>"


class PrzeplywMeasurement(Base):
    """Model pomiaru przepływu"""

    __tablename__ = "przeplyw_measurements"

    id = Column(
        String, primary_key=True
    )  # Możemy użyć kombinacji kod_stacji + timestamp jako id
    station_id = Column(String, ForeignKey("stations.id_stacji"), nullable=False)
    przeplyw_data = Column(DateTime, nullable=False)
    przelyw = Column(Float, nullable=False)

    # Relacja do stacji
    station = relationship("Station", back_populates="przeplyw_measurements")

    # Unikalny constraint na kombinację stacji i czasu
    __table_args__ = (
        UniqueConstraint(
            "station_id", "przeplyw_data", name="uix_station_przeplyw_time"
        ),
    )

    def __repr__(self):
        return f"<PrzeplywMeasurement(station_id='{self.station_id}', przeplyw_data='{self.przeplyw_data}')>"
