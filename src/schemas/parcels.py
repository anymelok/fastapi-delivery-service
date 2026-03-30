from typing import Union
from pydantic import BaseModel, Field
from typing import Any
from pydantic import ConfigDict, model_validator


class ParcelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    weight: float = Field(..., gt=0)
    type_id: int = Field(..., gt=0)
    price_usd: float = Field(..., gt=0)


class ParcelResponse(BaseModel):
    id: str
    name: str
    weight: float
    price_usd: float
    type_name: str
    delivery_cost: Union[float, str]

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def map_fields(cls, data: Any) -> Any:
        # Проверяем наличие атрибута, т.к. придет объект SQLAlchemy
        if hasattr(data, "parcel_type") and data.parcel_type:
            setattr(data, "type_name", data.parcel_type.name)

        # логика "Не рассчитано"
        cost = getattr(data, "delivery_cost_rub", None)
        setattr(data, "delivery_cost", cost if cost is not None else "Не рассчитано")

        return data
