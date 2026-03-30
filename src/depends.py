import uuid
from fastapi import Response, Cookie, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.repositories.parcels import ParcelRepository
from src.services.parcels import ParcelService


async def get_session_id(
    response: Response, session_id: str | None = Cookie(None)
) -> str:
    if not session_id:
        session_id = str(uuid.uuid4())
        # пихаем session_id в куки
        response.set_cookie(key="session_id", value=session_id, httponly=True)
    return session_id


def get_parcel_service(db: AsyncSession = Depends(get_session)) -> ParcelService:
    repo = ParcelRepository(db)
    return ParcelService(repo)
