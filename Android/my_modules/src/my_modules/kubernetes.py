from base64 import b64decode
from datetime import datetime
from json import loads
from subprocess import run
from typing import Literal

from my_modules.logger import status_decorator
from my_modules.process import wait_in_loop

RANCHER = "Rancher Desktop.exe"


def rancher_running() -> bool:
    """Function to check if Rancher Desktop is running.

    Returns:
        bool: True if running else False
    """
    return (
        RANCHER
        in run(
            f'tasklist | findstr "{RANCHER}"',
            shell=True,
            text=True,
            capture_output=True,
        ).stdout
    )


def node_ready() -> bool:
    """Function to check if AKS Node is in ready status.

    Returns:
        bool: True if ready else False
    """
    if (
        resp := run("kubectl get node", shell=True, capture_output=True, text=True)
    ).returncode != 0:
        return False
    else:
        return "Ready" in resp.stdout


@status_decorator("Rancher booting up...")
def wait_until_ready() -> None:
    """Function that keeps program wait until Rancher boots up."""
    started_at = datetime.now()
    while not (rancher_running() and node_ready()):
        wait_in_loop(started_at, wait=180, prompt="Rancher boot up failed.")


def get_json(
    name: str, resource: Literal["configmap", "secret"], base64decode: bool = False
) -> dict[str, str]:
    """Function to get kubernetes resource details in json format.

    Args:
        name (str): resource name.
        resource (Literal[&quot;configmap&quot;, &quot;secret&quot;]): resource type.
        base64decode (bool, optional): to decode base64 secrets, useful in parsing secrets. Defaults to False.

    Raises:
        Exception: If resource is not found.

    Returns:
        dict[str, str]: resource info.
    """
    if not node_ready():
        wait_until_ready()
    if (
        resp := run(
            f"kubectl get {resource} {name} -o jsonpath={{.data}}",
            shell=True,
            capture_output=True,
            text=True,
        )
    ).returncode == 0:
        data: dict[str, str] = loads(resp.stdout)
        if base64decode:
            data = {
                key: b64decode(value.encode()).decode() for key, value in data.items()
            }
        return data
    else:
        raise Exception(f"Resource named '{name}' is not found in '{resource}' type.")
