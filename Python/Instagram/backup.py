from datetime import datetime
from pathlib import Path
import shutil
import os
from send2trash import send2trash

def copy_directory(source_dir, destination_dir):
    # Ensure the source directory exists
    if not os.path.exists(source_dir):
        print(f"Source directory '{source_dir}' does not exist.")
        return
    
    # Ensure the destination directory exists or create it
    os.makedirs(destination_dir, exist_ok=True)
    
    # Copy all files and subdirectories
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        destination_item = os.path.join(destination_dir, item)
        
        if os.path.isdir(source_item):
            # Recursively copy subdirectories
            shutil.copytree(source_item, destination_item, dirs_exist_ok=True)
        else:
            # Copy individual files
            shutil.copy2(source_item, destination_item)


def rentention(n=10):
    bkp_dir = Path("Backups")
    expired_bkps = sorted(bkp_dir.iterdir(), reverse=True)[n:]
    list(map(send2trash, expired_bkps))

    
# Taking backup
source = "Profiles"
destination = Path("Backups") / f"Backup-{datetime.now().strftime("%Y%m%d%H%M%S")}"
Path(destination).mkdir(parents=True, exist_ok=True)
copy_directory(source, destination)
rentention()
