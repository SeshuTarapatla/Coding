from rich import print, traceback
from rich.console import Console
from sys import exit


console = Console()
console.clear()
traceback.install(show_locals=True)


class log:
    @staticmethod
    def error(msg: str):
        print(f"[red]ERROR[/]: {msg}")
        exit()
    
    @staticmethod
    def info(msg: str):
        print(f"[blue]INFO [/]: {msg}")
