from enum import Enum
from pathlib import PurePosixPath
from typing import Optional
import uiautomator2 as u2
from rich.status import Status

from utils import log


class Oneplus(u2.Device):
    def __init__(self):
        self.serial = "9cb9ec04"
        try:
            with Status("Connecting to Oneplus device"):
                super().__init__(self.serial)
                log.info(f"{self.info.get('productName')} is connected")
        except u2.ConnectError:
            log.error("ADB connection failed")

    def __call__(self, resourceId: Optional[Enum] = None, **kwargs) -> u2.UiObject:
        if isinstance(resourceId, Enum):
            return super().__call__(resourceId=resourceId.value, **kwargs)    
        elif isinstance(resourceId, str):
            return super().__call__(resourceId=resourceId)
        return super().__call__(**kwargs)
    
    def long_click(self, x: Optional[int] = None, y: Optional[int] = None, duration: float = 0.5):
        if not x:
            x = self.info['displayWidth']  // 2
        if not y:
            y = self.info['displayHeight'] // 2
        return super().long_click(x, y, duration)

    def count_dir(self, directory: PurePosixPath) -> int:
        count = len(self.list_dir(directory))
        return count

    def list_dir(self, directory: PurePosixPath) -> list:
        files = self.shell(f"find {directory} -type f").output.splitlines()
        return files
    
    def clean_dir(self, directory: PurePosixPath) -> None:
        self.shell(f"rm -rf {directory}/*")
        return None

oneplus = Oneplus()
