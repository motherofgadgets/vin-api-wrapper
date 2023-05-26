from fastapi import Depends, FastAPI, HTTPException
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
    db_vin = crud.get_decoded_vin(db, vin=vin)
    if db_vin is None:
        raise HTTPException(status_code=404, detail="VIN not found")
    return db_vin


@app.post("/vins/", response_model=schemas.DecodedVIN)
async def create_vin(vin: schemas.DecodedVINCreate, db: Session = Depends(get_db)):
    db_vin = crud.get_decoded_vin(db, vin=vin.vin)
    if db_vin:
        raise HTTPException(status_code=400, detail="VIN already added.")
    return crud.create_decoded_vin(db, vin=vin)


@app.get("/remove/{vin}")
async def remove(vin: str):
    return {"remove vin": vin}


@app.get("/export/")
async def export():
    return {"export": "complete"}
