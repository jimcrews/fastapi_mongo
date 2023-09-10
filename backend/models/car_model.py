from typing import Optional

from pydantic import Field, BaseModel

# from object_id_pydantic import ObjectIdStr
from bson import ObjectId


class CarBase(BaseModel):
    brand: str = Field(..., min_length=2)
    make: str = Field(..., min_length=1)
    year: int = Field(...)
    price: int = Field(...)
    km: int = Field(...)
    cm3: int = Field(..., gt=400, lt=8000)

    class Config:
        arbitrary_types_allowed = True


class CarWithId(CarBase):
    id: ObjectId = Field(alias="_id")


class CarUpdate(BaseModel):
    price: Optional[int] = None
