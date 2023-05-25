from fastapi import HTTPException
from sqlalchemy.orm import Session

from vindecode import models, schemas


def get_decoded_vin(db: Session, vin: str):
    return db.query(models.DecodedVIN).filter(models.DecodedVIN.vin == vin.upper()).first()


def create_decoded_vin(db: Session, vin: schemas.DecodedVINCreate):
    db_vin = models.DecodedVIN(
        vin=vin.vin,
        make=vin.make,
        model=vin.model,
        model_year=vin.model_year,
        body_class=vin.body_class
    )
    db.add(db_vin)
    db.commit()
    db.refresh(db_vin)
    return db_vin


def delete_decoded_vin(db: Session, vin: str):
    db_vin = db.get(schemas.DecodedVIN, vin.upper())
    if not db_vin:
        raise HTTPException(status_code=404, detail="VIN not found.")
    db.delete(db_vin)
    db.commit()
    return {"vin": vin, "deleted": True}