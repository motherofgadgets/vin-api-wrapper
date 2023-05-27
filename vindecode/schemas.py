from typing import Union

from pydantic import BaseModel


class DecodedVIN(BaseModel):
    vin: str
    make: Union[str, None] = None
    model: Union[str, None] = None
    model_year: Union[str, None] = None
    body_class: Union[str, None] = None
    cached: bool

    class Config:
        orm_mode = True
