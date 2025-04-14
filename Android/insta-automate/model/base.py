from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


schema: str = "instagram"
metadata = MetaData(schema=schema)

class Base(DeclarativeBase):
    metadata = metadata

