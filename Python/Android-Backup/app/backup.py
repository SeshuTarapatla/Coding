from datetime import datetime
from pathlib import Path, PurePosixPath
from shutil import move
from subprocess import run
from time import sleep
from typing import NamedTuple, cast

from colorama import Fore
from pandas import DataFrame, concat, read_csv

from app.render import Render
from app.vars import (
    DATAFRAME,
    DELTA_COLUMNS,
    DELTA_DATAFRAME,
    DELTA_DIR,
    DEVICE_DATAFRAME,
    DEVICE_ROOT,
    MYPASS,
    RAR_EXECUTABLE,
    RECYCLE_BIN,
)
from utils import UTF_8_SIG, log
from utils.android import device
from utils.terminal import colorize
from utils.thread import ExceptionalThread


def calculate_delta() -> None:
    """Function to calculate the delta between current backup and existing backup to perform minimal operations
    """
    # Separate stage to calculate delta
    log.stage("Delta")
    log.info("Calculating Delta for minimal operations")
    # variables
    src_file = DATAFRAME
    dst_file = DELTA_DATAFRAME
    cmp_file = DEVICE_DATAFRAME
    # read both dataframes
    current_df = read_csv(src_file, encoding=UTF_8_SIG)
    if cmp_file.exists():
        backed_up_df = read_csv(cmp_file, encoding=UTF_8_SIG)
    else:
        backed_up_df = DataFrame(columns=current_df.columns)
    # calculate delta as additions, deletions and modifications
    additions = current_df[~current_df["Path"].isin(backed_up_df["Path"])]
    deletions = backed_up_df[~backed_up_df["Path"].isin(current_df["Path"])]
    merged = current_df.merge(backed_up_df, on="Path", suffixes=("", "_old"))
    modifications = merged[(merged['Size'] != merged['Size_old']) | (merged['Date'] != merged['Date_old'])]
    # add operation tag as kind
    additions["Kind"] = "add"
    deletions["Kind"] = "remove"
    modifications['Kind'] = "modify"
    # concat into single delta frame and save
    delta_df = concat([additions, deletions, modifications])[DELTA_COLUMNS]
    delta_df.to_csv(dst_file, index=False, encoding=UTF_8_SIG)
    log.info(f"Delta DataFrame saved as   > {dst_file}")
    # print stats
    log.info(
        f"Total operations:          > "
        f"{colorize(len(delta_df), Fore.BLUE)} ["
        f"{colorize(f"+{len(additions)}", Fore.GREEN)}, "
        f"{colorize(f"~{len(modifications)}", Fore.YELLOW)}, "
        f"{colorize(f"-{len(deletions)}", Fore.RED)}]"
    )


class DeltaNamedTuple(NamedTuple):
    """A named tuple to enable typing hints for Deltaframe itertuples.
    """
    Index: int
    File: str
    Type: str
    Size: int
    Size_old: int
    Date: str
    Date_old: str
    Path: str
    Kind: str


class Delta:
    @staticmethod
    def delta() -> None:
        """Function to calculate the delta between current backup and existing backup to perform minimal operations
        """
        # Separate stage to calculate delta
        log.stage("Delta")
        log.info("Calculating Delta for minimal operations")
        # variables
        src_file = DATAFRAME
        dst_file = DELTA_DATAFRAME
        cmp_file = DEVICE_DATAFRAME
        # read both dataframes
        current_df = read_csv(src_file, encoding=UTF_8_SIG)
        if cmp_file.exists():
            backed_up_df = read_csv(cmp_file, encoding=UTF_8_SIG)
        else:
            backed_up_df = DataFrame(columns=current_df.columns)
        # calculate delta as additions, deletions and modifications
        additions = current_df[~current_df["Path"].isin(backed_up_df["Path"])]
        deletions = backed_up_df[~backed_up_df["Path"].isin(current_df["Path"])]
        merged = current_df.merge(backed_up_df, on="Path", suffixes=("", "_old"))
        modifications = merged[(merged['Size'] != merged['Size_old']) | (merged['Date'] != merged['Date_old'])]
        # add operation tag as kind
        additions["Kind"] = "add"
        deletions["Kind"] = "remove"
        modifications['Kind'] = "modify"
        # concat into single delta frame and save
        delta_df = concat([additions, deletions, modifications])[DELTA_COLUMNS]
        delta_df.to_csv(dst_file, index=False, encoding=UTF_8_SIG)
        log.info(f"Delta DataFrame saved as   > {dst_file}")
        # print stats
        log.info(
            f"Total operations:          > "
            f"{colorize(len(delta_df), Fore.BLUE)} ["
            f"{colorize(f"+{len(additions)}", Fore.GREEN)}, "
            f"{colorize(f"~{len(modifications)}", Fore.YELLOW)}, "
            f"{colorize(f"-{len(deletions)}", Fore.RED)}]"
        )


def delta_archive() -> None:
    current_date = datetime.now().strftime("%Y%m%d%H%M%S")
    rar_name = f"{DELTA_DIR.name}-{current_date}.rar"
    rar_path = DELTA_DIR.parent/rar_name
    args = [RAR_EXECUTABLE, "a", "-v1024m", f"-hp{MYPASS}", "-ep1", rar_path, DELTA_DIR]
    log.info(f"Archiving delta for online backup. Timestamp: {current_date}")
    run(args, shell=True)
    total_rars = len(list(filter(lambda x: x.suffix == ".rar", DELTA_DIR.parent.iterdir())))
    log.update(f"Archive complete. Total archives created: {total_rars}")


class session(Render):
    """Actual session of backup with live rendering of progress
    """
    def __init__(self) -> None:
        """Initializes all important variables both from parent `Render` class and current session variables like `deltaframe` & `progress bar tasks`
        """
        super().__init__()
        log.stage("Backup\n")
        self.deltaframe = read_csv(DELTA_DATAFRAME)
        self.total_size = sum(self.deltaframe["Size"])
        self.main_progress_task = self.main_progress_bar.add_task("main", total=self.total_size)
        self.panel_total = len(self.deltaframe)
        self.update_files_panel_title()
    
    def run_mock(self) -> None:
        """Function that mocks/simulates the process of pulling files. This is to develop/debug live render without actually pulling files.
        """
        for row in self.deltaframe.itertuples():
            # For each row/record in deltaframe mock the progress
            file = str(row.File)
            size = cast(int, row.Size)
            path = str(row.Path)
            kind = str(row.Kind)
            index = cast(int, row.Index)
            # Update panel render
            self.update_files_panel_title(index)
            self.insert_into_files_panel(path, kind)
            if size <= 100000000:
                # If file size <= 100MB simply pull the file in one go
                self.main_progress_bar.update(self.main_progress_task, advance=size)
                sleep(0.01)
            else:
                # Else simluate alt progress bar with custom sleep
                self.update_alt_progress_title(file)
                alt_task = self.alt_progress_bar.add_task(file, total=size)
                total = 0
                while not self.alt_progress_bar.finished:
                    total += 10000000
                    advance = min(total, size)
                    self.alt_progress_bar.update(alt_task, advance=advance)
                    self.main_progress_bar.update(self.main_progress_task, advance=advance)
                    sleep(0.1)
                self.alt_progress_bar.remove_task(alt_task)
                self.update_alt_progress_title()
    
    def run(self, mock: bool = False) -> None:
        """Start the backup session.

        Args:
            mock (bool, optional): Invokes run_mock() function instead of actual backup. Defaults to False.
        """
        if mock:
            self.run_mock()
            return
        # Initialize alt variables for thread pulls and progress bars
        self.alt_total = 0
        self.alt_size = 100_000_000 # alt size set to 100MB
        # Iterate over all files/rows
        for row in self.deltaframe.itertuples():
            # Casting row [PandasNamedTuple] in `DeltaNamedTuple` to enable type hints
            row = cast(DeltaNamedTuple, row)
            if row.Kind in ("add", "modify"):
                # if file is of kind add/modify pull the file from device
                self.fetch_file(row)
            elif row.Kind in ("remove"):
                # elif file is of kind remove move it to backup recycle bin folder
                self.recycle_file(row)
    
    def fetch_file(self, row: DeltaNamedTuple) -> None:
        """Function that fetches file in a given row from the dataframe

        Args:
            row (DeltaNamedTuple): Row from Delta frame itertuple
        """
        # Insert file into files panel
        self.insert_into_files_panel(row.Path, row.Kind)
        # calculate file paths for source and destination
        src_file = PurePosixPath(row.Path)
        dst_file = DELTA_DIR/src_file.relative_to(DEVICE_ROOT)
        # Create destination folder is not exists
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        if dst_file.exists() and dst_file.stat().st_size == row.Size:
            # if dst file already exists and file sizes matches, skip it
            self.main_progress_bar.update(self.main_progress_task, advance=row.Size)
        elif row.Size <= self.alt_size:
            # elif file size is less than alt_size [100mb] fetch the file [simple mode]
            self.fetch_file_simple(str(src_file), str(dst_file), row.Size)
        else:
            # else fecth the file in [threaded mode] with alt progress bar
            self.fetch_file_threaded(str(src_file), str(dst_file), row.Size)
        self.update_files_panel_title(row.Index+1)
    
    def fetch_file_simple(self, src_file: str, dst_file: str, progress: int) -> None:
        """Function that pulls file from device in simple mode.

        Args:
            src_file (str): input/source file path
            dst_file (str): output/destination file path
            progress (int): file size to update the main progress bar
        """
        device.pull(src_file, dst_file)
        self.main_progress_bar.update(self.main_progress_task, advance=progress)

    def fetch_file_threaded(self, src_file: str, dst_file: str, progress: int) -> None:
        """Function that pulls file from device in a separate thread. Function especially for large files whose size > alt_size [100MB], so that an alt_progress bar can be displayed for this single file.

        Args:
            src_file (str): input/source file path
            dst_file (str): output/destination file path
            progress (int): file size to update the main progress bar
        """
        # Set alt title and create a task for alt_progress bar
        self.update_alt_progress_title(src_file)
        alt_task = self.alt_progress_bar.add_task(src_file, total=progress)
        # Create a thread for pulling the file and start it
        thread = ExceptionalThread(target=device.pull, args=(src_file, dst_file))
        thread.start()
        file = Path(dst_file)
        # Store current progress value to update it at last
        current_total = self.main_progress_bar.tasks[self.main_progress_task].completed
        # Wait until a file placeholder is created at destination dir
        while True:
            if file.exists():
                break
        # While the thread is still active > fetch the file size and update alt_progress bar
        while thread.is_alive():
            alt_total = file.stat().st_size
            self.alt_progress_bar.update(alt_task, completed=alt_total)
            self.main_progress_bar.update(self.main_progress_task, completed=(current_total+alt_total))
        # Join the thread once done & reset alt_progress bar and title
        thread.join()
        self.alt_progress_bar.remove_task(alt_task)
        self.update_alt_progress_title()
        # Update main progress bar
        self.main_progress_bar.update(self.main_progress_task, completed=(current_total+progress))
    
    def recycle_file(self, row: DeltaNamedTuple) -> None:
        """Function that handles the rows of kind `remove`. It moves the file to a custom `Recycle Bin` folder within the backup dir.

        Args:
            row (DeltaNamedTuple): Row from Delta frame itertuple
        """
        self.insert_into_files_panel(row.Path, row.Kind)
        # Calculate all file paths
        src_file = PurePosixPath(row.Path)
        dst_file = DELTA_DIR/src_file.relative_to(DEVICE_ROOT)
        del_file = RECYCLE_BIN/dst_file.relative_to(DELTA_DIR)
        # Create a dir in `Recycle Bin` for the file if not exists
        del_file.parent.mkdir(parents=True, exist_ok=True)
        # Move the file and update the progress bars
        move(dst_file, del_file)
        self.main_progress_bar.update(self.main_progress_task, advance=row.Size)
        self.update_files_panel_title(row.Index)
