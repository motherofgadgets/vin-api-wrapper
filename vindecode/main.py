from fastapi import Depends, FastAPI
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
        # Call to VIN client goes here.
        new_db_vin = schemas.DecodedVIN(
            vin=vin,
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
    return crud.delete_decoded_vin(db, vin=vin)


@app.get("/export/")
async def export():
    return {"export": "complete"}
