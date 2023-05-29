import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from fastapi import Depends, FastAPI, Request, status, Path
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session

from vindecode import crud, models, schemas
from vindecode.database import SessionLocal, engine
from vindecode.vinextclient import VINExternalClient

models.Base.metadata.create_all(bind=engine)


class VINExternalClientException(Exception):
    """
    Represents an error returned from the External VIN API
    """

    def __init__(self, content: schemas.VINExternalClientError):
        self.content = content


app = FastAPI()


@app.exception_handler(VINExternalClientException)
async def ext_client_exception_handler(
    request: Request, exc: VINExternalClientException
):
    """
    Exception handler for errors returned from the External VIN API
    :param request: The incoming request
    :param exc: The exception raised.
    :return: The 400 response indicating a bad request with the content of the error
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder(exc.content)
    )


def get_db():
    """
    Obtains an independent database connection. Allows dependency override.
    :return: A database session that is closed when a request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_external_client():
    """
    Obtains an HTTP Client to call the external VIN API
    :return: The HTTP Client
    """
    return VINExternalClient()


@app.get("/")
async def root():
    """
    A basic message when no other endpoints are specified
    """
    return {"message": "Welcome to the Vin Decode Application!"}


@app.get(
    "/lookup/{vin}",
    response_model=schemas.DecodedVIN,
    responses={400: {"model": schemas.VINExternalClientError}},
)
async def lookup(
    vin: str = Path(min_length=17, max_length=17, regex="^[a-zA-Z0-9]"),
    db: Session = Depends(get_db),
    ext_client: VINExternalClient = Depends(get_external_client),
):
    """
    Checks the cache for the existing DecodedVIN record by VIN number. If that VIN is not cached, makes a call
    to the external VIN API, and saves the results in the cache before returning.
    :param vin: 17-digit alphanumeric string
    :param db: database connection
    :param ext_client: the client to call the external VIN API
    :return: A Decoded VIN
    """
    # Check the cache for the VIN
    db_vin = crud.get_decoded_vin(db, vin=vin.upper())

    if db_vin is None:
        # Call the External VIN API
        ext_response = ext_client.get_vin(vin)
        if ext_response["ErrorCode"] == "0":
            new_db_vin = schemas.DecodedVIN(
                vin=vin.upper(),
                make=ext_response["Make"],
                model=ext_response["Model"],
                model_year=ext_response["ModelYear"],
                body_class=ext_response["BodyClass"],
                cached=False,
            )
            return crud.create_decoded_vin(db, vin=new_db_vin)
        else:
            # If there is an error in the VIN, the API will respond with status code 200,
            # but the actual error code will be in the data
            error_msg = schemas.VINExternalClientError(
                ErrorCode=ext_response["ErrorCode"],
                ErrorText=ext_response["ErrorText"],
                AdditionalErrorText=ext_response["AdditionalErrorText"],
            )
            raise VINExternalClientException(error_msg)
    return db_vin


@app.delete(
    "/remove/{vin}",
    response_model=schemas.DeleteVinSuccess,
    responses={404: {"detail": "VIN not found."}},
)
async def remove(
    vin: str = Path(min_length=17, max_length=17, regex="^[a-zA-Z0-9]"),
    db: Session = Depends(get_db),
):
    """
    Removes a DecodedVIN record from the cache.
    :param vin: 17-digit alphanumeric string
    :param db: database connection
    :return: Message confirming deletion
    """
    return crud.delete_decoded_vin(db, vin=vin.upper())


@app.get("/export/", response_class=StreamingResponse)
async def export(db: Session = Depends(get_db)):
    """
    Exports the cache in a parquet file
    :param db: database connection
    :return: A parquet file containing all records in the cache
    """
    vins = crud.get_all_vins(db)

    # Read the query data to a DataFrame
    df = pd.read_sql(vins.statement, vins.session.bind)
    table = pa.Table.from_pandas(df)

    # Write the DataFrame to a streaming parquet file
    buffer = pa.BufferOutputStream()
    pq.write_table(table, buffer)
    response = StreamingResponse(
        iter([buffer.getvalue().to_pybytes()]), media_type="application/octet-stream"
    )
    response.headers["Content-Disposition"] = "attachment; filename=export.parquet"

    return response
