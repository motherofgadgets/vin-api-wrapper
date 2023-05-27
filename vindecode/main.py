import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from vindecode import crud, models, schemas
from vindecode.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Welcome to the Vin Decode Application!"}


@app.get("/lookup/{vin}", response_model=schemas.DecodedVIN)
async def lookup(vin: str, db: Session = Depends(get_db)):
    db_vin = crud.get_decoded_vin(db, vin=vin.upper())
    if db_vin is None:
        # Call to VIN client goes here.
        new_db_vin = schemas.DecodedVIN(
            vin=vin.upper(),
            make="PETERBILT",
            model="388",
            model_year="2014",
            body_class="Truck-Tractor",
            cached=False
        )
        return crud.create_decoded_vin(db, vin=new_db_vin)
    return db_vin


@app.delete("/remove/{vin}")
async def remove(vin: str, db: Session = Depends(get_db)):
    return crud.delete_decoded_vin(db, vin=vin.upper())


@app.get("/export/")
async def export(db: Session = Depends(get_db)):
    vins = crud.get_all_vins(db)
    df = pd.read_sql(vins.statement, vins.session.bind)
    table = pa.Table.from_pandas(df)
    buffer = pa.BufferOutputStream()
    pq.write_table(table, buffer)
    response = StreamingResponse(iter([buffer.getvalue().to_pybytes()]), media_type="application/octet-stream")
    response.headers["Content-Disposition"] = "attachment; filename=export.parquet"

    return response
