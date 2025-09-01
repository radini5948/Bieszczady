# Nowy plik: flood_monitoring/models/warnings.py
"""
Modele dla ostrzeżeń hydrologicznych
"""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY

from flood_monitoring.core.database import Base


class HydroWarning(Base):
    """Model ostrzeżenia hydrologicznego"""

    __tablename__ = "hydro_warnings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    opublikowano = Column(DateTime, nullable=False)
    stopien = Column(String, nullable=False)
    data_od = Column(DateTime, nullable=False)
    data_do = Column(DateTime, nullable=False)
    prawdopodobienstwo = Column(String, nullable=False)
    numer = Column(String, nullable=False)
    biuro = Column(String, nullable=False)
    zdarzenie = Column(String, nullable=False)
    przebieg = Column(Text, nullable=False)
    komentarz = Column(Text, nullable=False)

    # Relacja do obszarów
    areas = relationship("WarningArea", back_populates="warning")

    def __repr__(self):
        return f"<HydroWarning(numer='{self.numer}', zdarzenie='{self.zdarzenie}')>"


class WarningArea(Base):
    """Model obszaru ostrzeżenia"""

    __tablename__ = "warning_areas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    warning_id = Column(Integer, ForeignKey("hydro_warnings.id"), nullable=False)
    wojewodztwo = Column(String, nullable=False)
    opis = Column(String, nullable=False)
    kod_zlewni = Column(ARRAY(String), nullable=False)

    # Relacja do ostrzeżenia
    warning = relationship("HydroWarning", back_populates="areas")

    def __repr__(self):
        return f"<WarningArea(wojewodztwo='{self.wojewodztwo}', opis='{self.opis}')>"