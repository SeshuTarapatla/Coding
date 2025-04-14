from concurrent.futures import ThreadPoolExecutor
# from os import system
from threading import Lock

from tqdm import tqdm
from xxhash import xxh64
from model import session, Media
from rich import traceback

traceback.install(show_locals=True)

# system("cls")
print("Stage: FILE HASH")
tqdm.set_lock(Lock())

sql = session.query(Media).where(Media.file_hash.is_(None))
print(f"Total media files: {sql.count()}")

def file_hash(row: Media, pbar: tqdm) -> str:
    hasher = xxh64()
    with open(row.path, "rb") as f:
        [hasher.update(chunk) for chunk in iter(lambda: f.read(100_000_000), b"")]
    pbar.update()
    return hasher.hexdigest()

with tqdm(total=sql.count(), desc="Calculating file hash") as pbar:
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda row: file_hash(row, pbar), sql))

for row, result in tqdm(zip(sql, results), total=sql.count(), desc="Updating db"):
    row.file_hash = result
    session.merge(row)
session.commit()
print("Stage complete")
