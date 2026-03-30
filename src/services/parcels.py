from typing import Sequence
from src.repositories.models import Parcel, ParcelType
from src.repositories.parcels import ParcelRepository
import uuid
from src.services.external import get_usd_rate


class ParcelService:
    def __init__(self, repo: ParcelRepository) -> None:
        self.repo = repo

    async def create_parcel(self, session_id: str, data: dict) -> str:
        """Создаёт посылку и возвращает id"""
        parcel_id = str(uuid.uuid4())

        full_data = {"id": parcel_id, "session_id": session_id, **data}
        await self.repo.create(full_data)

        return parcel_id

    async def get_my_parcels(
        self,
        session_id: str,
        limit: int,
        offset: int,
        type_id: int | None,
        is_calculated: bool | None,
    ) -> Sequence[Parcel]:
        parcels = await self.repo.get_my_parcels(
            session_id=session_id,
            limit=limit,
            offset=offset,
            type_id=type_id,
            is_calculated=is_calculated,
        )

        return parcels

    async def get_parcel_by_id(self, parcel_id: str, session_id: str) -> Parcel | None:
        """
        Получение посылки по id
        Для получения нужно быть владельцем посылки
        """
        parcel = await self.repo.get_by_id(parcel_id=parcel_id)
        if parcel is not None:
            if parcel.session_id != session_id:
                raise PermissionError("This is not your parcel")
            return parcel
        return None

    async def get_types(self) -> Sequence[ParcelType]:
        """Получение списка всех типов посылок"""
        types = await self.repo.get_types()
        return types

    async def calculate_delivery_costs(self) -> None:
        """Просчёт стоимости доставки для посылок"""
        usd_rate = await get_usd_rate()
        parcels = await self.repo.get_unprocessed_parcels()

        if not parcels:
            return

        for parcel in parcels:
            cost = (parcel.weight * 0.5 + parcel.price_usd * 0.01) * usd_rate
            parcel.delivery_cost_rub = round(cost, 2)

        await self.repo.save_all()
        return
