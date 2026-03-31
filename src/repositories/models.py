from typing import Optional
from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ParcelType(Base):
    __tablename__ = "parcel_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[int] = mapped_column(String(50), unique=True)

    parcels: Mapped[list["Parcel"]] = relationship(back_populates="parcel_type")


class Parcel(Base):
    __tablename__ = "parcels"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)

    name: Mapped[str] = mapped_column(String(255))
    weight: Mapped[float] = mapped_column(Float)
    price_usd: Mapped[float] = mapped_column(Float)
    delivery_cost_rub: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    type_id: Mapped[int] = mapped_column(ForeignKey("parcel_types.id"))

    # для удобства получения имени типа
    parcel_type: Mapped["ParcelType"] = relationship(back_populates="parcels")
