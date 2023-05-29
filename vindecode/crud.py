from fastapi import HTTPException
from sqlalchemy.orm import Session

from vindecode import models, schemas


def get_decoded_vin(db: Session, vin: str):
    """
    Gets a single DecodedVIN object by its VIN
    :param db: database connection
    :param vin: 17-digit alphanumeric string
    :return: a DecodedVIN
    """
    return db.query(models.DecodedVIN).filter(models.DecodedVIN.vin == vin).first()


def get_all_vins(db: Session):
    """
    Gets all cached DecodedVIN objects
    :param db: database connection
    :return: All DecodedVIN objects
    """
    return db.query(models.DecodedVIN)


def create_decoded_vin(db: Session, vin: schemas.DecodedVIN):
    """
    Adds a DecodedVIN to the cache
    :param db: database connection
    :param vin: a DecodedVIN
    :return: a DecodedVIN
    """
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

    # We're returning the input schema because this object was not cached at the time the request was made
    return vin


def delete_decoded_vin(db: Session, vin: str):
    """
    Deletes a DecodedVIN from the cache
    :param db: database connection
    :param vin: a DecodedVIN
    :return: Message indicating record deletion
    """
    db_vin = get_decoded_vin(db, vin)
    if not db_vin:
        raise HTTPException(status_code=404, detail="VIN not found.")
    db.delete(db_vin)
    db.commit()
    return schemas.DeleteVinSuccess(vin=vin, deleted=True)
