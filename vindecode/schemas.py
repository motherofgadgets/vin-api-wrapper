from typing import Union

from pydantic import BaseModel


class DecodedVINBase(BaseModel):
    vin: str
    make: Union[str, None] = None
    model: Union[str, None] = None
    model_year: Union[str, None] = None
    body_class: Union[str, None] = None


class DecodedVINCreate(DecodedVINBase):
    pass


class DecodedVIN(DecodedVINBase):
    class Config:
        orm_mode = True
