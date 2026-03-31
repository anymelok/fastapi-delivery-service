from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from src.schemas.parcels import ParcelCreate, ParcelResponse
from src.services.parcels import ParcelService
from src.depends import get_parcel_service, get_session_id

router = APIRouter(prefix="/parcels", tags=["Parcels"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def register_parcel(
    data: ParcelCreate,
    service: ParcelService = Depends(get_parcel_service),
    session_id: str = Depends(get_session_id),
):
    """
    ## Регистрация посылки \n
    ### В теле запроса указывается **ParcelCreate**  \n
    """
    # model_dump() делает из Pydantic dict
    parcel_id = await service.create_parcel(session_id, data.model_dump())
    return {"id": parcel_id}


@router.get("/", response_model=list[ParcelResponse])
async def list_my_parcels(
    limit: int = 10,
    offset: int = 0,
    type_id: int | None = None,
    is_calculated: bool | None = None,
    service: ParcelService = Depends(get_parcel_service),
    session_id: str = Depends(get_session_id),
):
    """
    ## Вывод списка всех посылок пользователя   \n
    ### Использует id сессии для определения владельца посылки
    """
    parcels = await service.get_my_parcels(
        session_id=session_id,
        limit=limit,
        offset=offset,
        type_id=type_id,
        is_calculated=is_calculated,
    )

    return parcels


@router.get("/types")
async def get_types(
    service: ParcelService = Depends(get_parcel_service),
):
    """
    ## Получение всех возможных типов посылок
    """
    types = await service.get_types()
    return types


@router.get("/{parcel_id}", response_model=ParcelResponse)
async def get_parcel_by_id(
    parcel_id: str,
    service: ParcelService = Depends(get_parcel_service),
    session_id: str = Depends(get_session_id),
):
    """
    ## Получение посылки по её id \n
    ### Использует id сессии для определения владельца \n
    В случае несовпадения id владельца выводит 403
    """
    try:
        parcel = await service.get_parcel_by_id(
            parcel_id=parcel_id, session_id=session_id
        )
        if not parcel:
            raise HTTPException(status_code=404, detail="Parcel not found")
        return parcel
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/tasks/run-calculation")
async def run_delivery_costs_calculation(
    service: ParcelService = Depends(get_parcel_service),
):
    """
    ## Запуск просчёта стоимости посылок вне расписания
    ### По расписанию просчёт делается каждые 5 минут
    """
    await service.calculate_delivery_costs()
