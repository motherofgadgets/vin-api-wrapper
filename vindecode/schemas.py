from typing import Union

from pydantic import BaseModel


class DecodedVIN(BaseModel):
    """
    The data of a decoded VIN as reported from the VIN API
    """

    vin: str
    make: Union[str, None] = None
    model: Union[str, None] = None
    model_year: Union[str, None] = None
    body_class: Union[str, None] = None
    cached: bool

    class Config:
        orm_mode = True


class DeleteVinSuccess(BaseModel):
    """
    The message returned when a DecodedVIN has been deleted successfully
    """

    vin: str
    deleted: bool = True


class VINExternalClientError(BaseModel):
    """
    The message returned when the External VIN API returns with status code 200 but an error in the content.
    """

    ErrorCode: Union[str, None] = None
    ErrorText: Union[str, None] = None
    AdditionalErrorText: Union[str, None] = None

    class Config:
        schema_extra = {
            "example": {
                "ErrorCode": "1",
                "ErrorText": "1 - Check Digit (9th position) does not calculate properly",
                "AdditionalErrorText": "",
            }
        }
