from fastapi import FastAPI

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


@app.get("/lookup/{vin}")
async def lookup(vin: str):
    return {"vin": vin}


@app.get("/remove/{vin}")
async def remove(vin: str):
    return {"remove vin": vin}


@app.get("/export/")
async def export():
    return {"export": "complete"}
