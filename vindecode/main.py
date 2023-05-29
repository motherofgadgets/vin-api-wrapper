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
    def __init__(self, content: schemas.VINExternalClientError):
        self.content = content


app = FastAPI()


@app.exception_handler(VINExternalClientException)
async def ext_client_exception_handler(request: Request, exc: VINExternalClientException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(exc.content)
    )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_external_client():
    return VINExternalClient()


@app.get("/")
async def root():
    return {"message": "Welcome to the Vin Decode Application!"}


@app.get("/lookup/{vin}", response_model=schemas.DecodedVIN, responses={400: {"model": schemas.VINExternalClientError}})
async def lookup(vin: str = Path(min_length=17, max_length=17, regex="^[a-zA-Z0-9]"), db: Session = Depends(get_db),
                 ext_client: VINExternalClient = Depends(get_external_client)):
    db_vin = crud.get_decoded_vin(db, vin=vin.upper())
    if db_vin is None:
        ext_response = ext_client.get_vin(vin)
        if ext_response["ErrorCode"] == '0':
            new_db_vin = schemas.DecodedVIN(
                vin=vin.upper(),
                make=ext_response["Make"],
                model=ext_response["Model"],
                model_year=ext_response["ModelYear"],
                body_class=ext_response["BodyClass"],
                cached=False
            )
            return crud.create_decoded_vin(db, vin=new_db_vin)
        else:
            error_msg = schemas.VINExternalClientError(
                ErrorCode=ext_response["ErrorCode"],
                ErrorText=ext_response["ErrorText"],
                AdditionalErrorText=ext_response["AdditionalErrorText"]
            )
            raise VINExternalClientException(error_msg)
    return db_vin


@app.delete("/remove/{vin}", response_model=schemas.DeleteVinSuccess, responses={404: {"detail": "VIN not found."}})
async def remove(vin: str = Path(min_length=17, max_length=17, regex="^[a-zA-Z0-9]"), db: Session = Depends(get_db)):
    return crud.delete_decoded_vin(db, vin=vin.upper())


@app.get("/export/", response_class=StreamingResponse)
async def export(db: Session = Depends(get_db)):
    vins = crud.get_all_vins(db)
    df = pd.read_sql(vins.statement, vins.session.bind)
    table = pa.Table.from_pandas(df)
    buffer = pa.BufferOutputStream()
    pq.write_table(table, buffer)
    response = StreamingResponse(iter([buffer.getvalue().to_pybytes()]), media_type="application/octet-stream")
    response.headers["Content-Disposition"] = "attachment; filename=export.parquet"

    return response
