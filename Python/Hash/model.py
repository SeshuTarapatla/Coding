from atexit import register
from datetime import datetime
from pathlib import Path
from pprint import pformat
from typing import Any, Literal

from humanize import naturalsize
from sqlalchemy import BigInteger, DateTime, Dialect, String, Text, TypeDecorator, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

all_dirs: list[Path] = [
    Path(r"C:\Users\seshu\Pictures"),
    Path(r"C:\Users\seshu\Documents"),
    Path(r"D:\Backup"),
    Path(r"D:\Projects\Legacy\Android-Backup-Tool\I2201"),
    Path(r"D:\Projects\Legacy\Android-Backup-Tool\ONEPLUS A6000"),
    Path(r"D:\RAW"),
]

img_types = ["cr2", "gif", "heic", "jpeg", "jpg", "png", "webp"]
vid_types = ["mkv", "mov", "mp4", "webm"]
all_types = img_types + vid_types

def ext(file: Path | str) -> str:
    file = file if isinstance(file, Path) else Path(file)
    return file.suffix.lower().lstrip(".")

class Base(DeclarativeBase): ...

class PathType(TypeDecorator):
    impl = Text
    cache_ok = True
    
    def process_bind_param(self, value: Path | None, dialect: Dialect) -> str | None:
        return value.as_posix() if isinstance(value, Path) else None

    def process_result_value(self, value: str | None, dialect: Dialect) -> Path | None:
        return Path(value) if isinstance(value, str) else None

class Media(Base):
    __tablename__ = "google_photos"
    filename: Mapped[str] = mapped_column(Text)
    path: Mapped[Path] = mapped_column(PathType, primary_key=True)
    type: Mapped[str] = mapped_column(String(4))
    size: Mapped[int] = mapped_column(BigInteger)
    size_norm: Mapped[str] = mapped_column(String(16))
    media: Mapped[Literal["image", "video"]] = mapped_column(String(5))
    modify_date: Mapped[datetime] = mapped_column(DateTime)
    exif_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    file_hash: Mapped[str | None] = mapped_column(String(16), nullable=True)
    media_hash: Mapped[str | None] = mapped_column(String(16), nullable=True)
    exif_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    def __init__(self, path: Path, **kw: Any):
        super().__init__(**kw)
        stat = path.stat()
        self.path = path
        self.filename = path.name
        self.type = ext(path)
        self.size = stat.st_size
        self.size_norm = naturalsize(self.size)
        self.modify_date = datetime.fromtimestamp(int(stat.st_mtime))
        if self.type in img_types:
            self.media = "image"
        elif self.type in vid_types:
            self.media = "video"
    
    def __str__(self) -> str:
        return pformat(self.__dict__)

    def __repr__(self) -> str:
        return self.__str__()

connection_string = "postgresql+psycopg2://seshu:28324630@localhost:30001/database"
engine = create_engine(url=connection_string)
Session = sessionmaker(bind=engine)
session = Session()
register(session.close_all)
Base.metadata.create_all(bind=engine)
