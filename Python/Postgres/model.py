from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


POSTGRES_USERNAME = "seshu"
POSTGRES_PASSWORD = "28324630"
POSTGRES_DATABASE = "database"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 30001

connection_string = f"postgresql+psycopg2://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
print(f"{connection_string=}")

class Base(DeclarativeBase): ...

class Secret(Base):
    __tablename__ = "secrets"
    filename: Mapped[str] = mapped_column(Text)
    secret: Mapped[dict] = mapped_column(JSONB)
    __mapper_args__ = {
        "primary_key": []
    }