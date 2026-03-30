from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.models import Parcel, ParcelType


class ParcelRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> Parcel:
        """
        Добавить посылку в бд
        """
        new_parcel = Parcel(**data)

        self.session.add(new_parcel)
        await self.session.commit()
        await self.session.refresh(new_parcel)
        return new_parcel

    async def get_types(self):
        """
        Возвращает все типы из таблицы parcel_types
        """
        result = await self.session.execute(select(ParcelType))
        return result.scalars().all()

    async def get_my_parcels(
        self,
        session_id: str,
        limit: int,
        offset: int,
        type_id: int | None = None,
        is_calculated: bool | None = None,
    ):
        """
        Возвращает все посылки пользователя
        """
        query = (
            select(Parcel)
            .where(Parcel.session_id == session_id)
            .options(joinedload(Parcel.parcel_type))
        )

        if type_id:
            query = query.where(Parcel.type_id == type_id)

        if is_calculated:
            query = query.where(Parcel.delivery_cost_rub.is_not(None))
        # elif is_calculated == False:
        #     query = query.where(Parcel.delivery_cost_rub.is_(None))

        result = await self.session.execute(query.limit(limit).offset(offset))

        return result.scalars().all()

    async def get_by_id(self, parcel_id: str) -> Parcel | None:
        """Получить посылку по id"""
        result = await self.session.execute(
            select(Parcel)
            .where(Parcel.id == parcel_id)
            .options(joinedload(Parcel.parcel_type))
        )
        return result.scalar_one_or_none()

    async def get_unprocessed_parcels(self) -> Sequence[Parcel]:
        query = select(Parcel).where(Parcel.delivery_cost_rub.is_(None))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save_all(self) -> None:
        await self.session.commit()
