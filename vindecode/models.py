from sqlalchemy import Column, String, Boolean

from vindecode.database import Base


class DecodedVIN(Base):
    """
    The data of a decoded VIN as reported from the VIN API
    """

    __tablename__ = "decoded_vins"

    vin = Column(String, primary_key=True, index=False)
    make = Column(String)
    model = Column(String)
    model_year = Column(String)
    body_class = Column(String)
    cached = Column(Boolean, default=True)
