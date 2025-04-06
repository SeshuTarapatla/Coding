from datetime import datetime
from time import sleep

import pyautogui as ag
import pygetwindow as gw

from my_modules.logger import status_decorator
from my_modules.process import spawn_windows_process


@status_decorator("Starting emulator")
def start(emulator: str = "emulator", snap_to_zone: bool = True) -> None:
    """Start the android emulator qemu session.

    Args:
        emulator (str, optional): emulator name. Defaults to "emulator".
        snap_to_zone (bool, optional): snapt to fancy zone. Defaults to True.

    Raises:
        TimeoutError: If window doesn't spawn under 30 seconds.
        ValueError: If multiple instances of emulator are found.
    """
    def emu_window() -> list[gw.Win32Window]:
        "Helper function that returns emulator window title as list."
        return gw.getWindowsWithTitle(f"Android Emulator - {emulator}:")

    # start the emulator if not running:    
    if not emu_window():
        spawn_windows_process(
            f"emulator -avd {emulator} -gpu host -no-audio",
            minimized=True,
            title="emulator-console",
        )
    # wait for it to spawn
    started_at = datetime.now()
    time_limit: float = 30
    while not (windows := emu_window()):
        sleep(1)
        if (datetime.now() - started_at).seconds > time_limit:
            raise TimeoutError("Failed to fetch the window of emulator.")
    if len(windows) == 1:
        window = windows[0]
    else:
        raise ValueError("Multiple instances of emulator found.")
    # snap it into fancy zones
    if snap_to_zone:
        if window.isMinimized:
            window.restore()
        window.activate()
        if window.top < 0:
            ag.click(window.left + 2, window.bottom - 2)
            ag.sleep(0.5)
        if not window.box == (1866, 0, 685, 1537):
            ag.keyDown("shift")
            ag.moveTo(window.left + 50, window.top + 30)
            ag.mouseDown()
            ag.moveTo(2000, 500)
            ag.mouseUp()
            ag.keyUp("shift")
