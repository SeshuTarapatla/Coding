from datetime import datetime
from subprocess import DEVNULL, STARTF_USESHOWWINDOW, STARTUPINFO, SW_HIDE, Popen
from time import sleep


def spawn_windows_process(cmd: str, title: str = "", minimized: bool = False) -> Popen[bytes]:
    """Spawn the given windows process in a new shell.

    Args:
        cmd (str): command arguments in a string.
        title (str, optional): title of the console. Defaults to "".
        minimized (bool, optional): minimize the console window. Defaults to False.

    Returns:
        Popen[bytes]: subprocess.Popen object
    """
    startupinfo = STARTUPINFO()
    startupinfo.dwFlags |= STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = SW_HIDE
    args = " ".join(["start", f'"{title}"', ("/min" if minimized else ""), cmd])
    process = Popen(
        args=args, shell=True, stdout=DEVNULL, stderr=DEVNULL, startupinfo=startupinfo
    )
    return process

def wait_in_loop(start: datetime, wait: float = 30, prompt: str = "") -> None:
    """Function to keep program wait inside a loop

    Args:
        start (datetime): loop started at.
        wait (float): wait in seconds. Defaults to 30.
        prompt (str): error message.
    Raises:
        TimeoutError: time limit exceeded.
    """
    sleep(1)
    if (datetime.now() - start).seconds >= wait:
        raise TimeoutError(f"Time limit exceeded. {prompt}")
