from datetime import datetime
from json import loads
# from os import system
from pathlib import Path
from shutil import copy2
from subprocess import check_output
from send2trash import send2trash
from tqdm import tqdm
from model import session, Media
from exiftool import ExifToolHelper
from rich import traceback

traceback.install(show_locals=True)
# system("cls")
print("Stage: EXIF DATA")

sql = session.query(Media).where(Media.exif_data.is_(None))
et = ExifToolHelper()

print(f"Total media files: {sql.count()}")
for row in tqdm(sql, total=sql.count(), desc="Fecthing metadata", unit="files"):
    if row.exif_data is not None:
        continue
    try:
        md: dict[str, str] = et.get_metadata(row.path.as_posix())[0]
    except (UnicodeDecodeError, UnicodeEncodeError):
        copy2(row.path, "cache")
        try:
            md: dict[str, str] = et.get_metadata("cache")[0]
        except UnicodeDecodeError:
            md = loads(check_output(args=["exiftool", "-json", row.path.as_posix()], text=True, encoding="utf-8").lstrip("[").rstrip("]\n"))
    except Exception as ext:
        print(ext)
        continue
    tag = ""
    if row.media == "image":
        tag = "EXIF:DateTimeOriginal"
    elif row.media == "video":
        tag = "QuickTime:CreateDate"
    if dt := md.get(tag, ""):
        try:
            row.exif_date = datetime.strptime(dt.replace("-",":"), "%Y:%m:%d %H:%M:%S")
        except Exception:
            row.exif_date = None
    row.exif_data = md
    session.merge(row)

print("Updating db")
send2trash("cache") if Path("cache").exists() else None
et.terminate()
session.commit()
print("Stage complete")
