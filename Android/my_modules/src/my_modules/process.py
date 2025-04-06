from subprocess import DEVNULL, STARTF_USESHOWWINDOW, STARTUPINFO, SW_HIDE, Popen


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
