from concurrent.futures import ThreadPoolExecutor
# from os import system
from threading import Lock
from types import NoneType

from PIL import Image
from pillow_heif import register_heif_opener
from cv2 import CAP_PROP_FRAME_COUNT, CAP_PROP_POS_FRAMES, COLOR_BGR2RGB, VideoCapture, cvtColor
from tqdm import tqdm
from xxhash import xxh64

from model import Media, session
from rich import traceback

traceback.install(show_locals=True)
# system("cls")
print("Stage: MEDIA HASH")
register_heif_opener()
tqdm.set_lock(Lock())

sql = session.query(Media).where(Media.media_hash.is_(None))
print(f"Total media files: {sql.count()}")

def media_hash(row: Media, pbar: tqdm) -> str | None:
    hash = None
    try:
        if row.media == "image":
            img = Image.open(row.path)
            hash = xxh64(img.tobytes()).hexdigest()
        elif row.media == "video":
            cap = VideoCapture(row.path.as_posix())
            frames = int(cap.get(CAP_PROP_FRAME_COUNT))
            cap.set(CAP_PROP_POS_FRAMES, frames//2)
            ret, frame = cap.read()
            cap.release()
            if not ret:
                cap = VideoCapture(row.path.as_posix())
                for _ in range((frames//2)+1):
                    ret, frame = cap.read()
            if not isinstance(frame, NoneType):
                img = Image.fromarray(cvtColor(frame, COLOR_BGR2RGB))
                hash = xxh64(img.tobytes()).hexdigest()
        pbar.update(1)
    except OSError:
        pass
    return hash

with tqdm(total=sql.count(), desc="Calculating media hash") as pbar:
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda row: media_hash(row, pbar), sql))

for row, result in tqdm(zip(sql, results), total=sql.count(), desc="Updating db"): # type: ignore
    row.media_hash = result
    session.merge(row)
session.commit()
print("Stage complete")
