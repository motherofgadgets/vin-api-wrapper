from fastapi import HTTPException
from sqlalchemy.orm import Session

from vindecode import models, schemas


def get_decoded_vin(db: Session, vin: str):
    return db.query(models.DecodedVIN).filter(models.DecodedVIN.vin == vin).first()


def get_all_vins(db: Session):
    return db.query(models.DecodedVIN)


def create_decoded_vin(db: Session, vin: schemas.DecodedVIN):
    db_vin = models.DecodedVIN(
        vin=vin.vin,
        make=vin.make,
        model=vin.model,
        model_year=vin.model_year,
        body_class=vin.body_class,
    )
    db.add(db_vin)
    db.commit()
    db.refresh(db_vin)
    return vin


def delete_decoded_vin(db: Session, vin: str):
    db_vin = get_decoded_vin(db, vin)
    if not db_vin:
        raise HTTPException(status_code=404, detail="VIN not found.")
    db.delete(db_vin)
    db.commit()
    return {"vin": vin, "deleted": True}
