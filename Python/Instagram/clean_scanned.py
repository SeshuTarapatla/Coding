from pathlib import Path


scanned_users_file = Path("./Profiles/scanned.users")
with open(scanned_users_file,"r+") as file:
    data = set(file.read().splitlines())
    file.seek(0)
    file.truncate()
    file.write("\n".join(sorted(data) + [""]))
    