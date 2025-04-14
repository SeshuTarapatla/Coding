from concurrent.futures import ThreadPoolExecutor
from itertools import chain
# from os import system
from pathlib import Path
from pandas import DataFrame, read_sql
from tqdm import tqdm
from model import Media, all_dirs, ext, all_types, session, engine
from rich import traceback

traceback.install(show_locals=True)

# system("cls")
print("Stage: REFRESH DB\n")

print("Loading current database: ", end="", flush=True)
db = read_sql("google_photos", con=engine)
db["path"] = db["path"].apply(Path) # type: ignore
print(f"{len(db)} rows")

print("Creating dirs dataframe : ", end="", flush=True)
df = DataFrame()
df["path"] = list(filter(lambda x: x.is_file(), chain(*[dir.rglob("*") for dir in all_dirs])))
df["type"] = df["path"].apply(ext)
df = df[df["type"].isin(all_types)].reset_index(drop=True)
print(f"{len(df)} rows\n")

merged = db.merge(df, on="path", how="outer", indicator=True)
append = merged[merged["_merge"] == "right_only"]
remove = merged[merged["_merge"] == "left_only"]
print(f"New rows: {len(append)} | Delete rows: {len(remove)}")
print("Updating db")

def MediaInit(file: Path, pbar: tqdm) -> Media:
    obj = Media(file)
    pbar.update(1)
    return obj

with tqdm(total=len(append), desc="Adding new rows", unit="files") as pbar:
    with ThreadPoolExecutor() as executor: 
        results = list(executor.map(lambda file: MediaInit(file, pbar), append["path"]))
session.add_all(results)

remove_rows = session.query(Media).where(Media.path.in_(remove["path"])).all()
[session.delete(row) for row in tqdm(remove_rows, total=len(remove), desc="Remove old rows", unit="files")]
print("Committing changes")
session.commit()

print("Stage complete")
