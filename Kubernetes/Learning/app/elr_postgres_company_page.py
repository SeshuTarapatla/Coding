from argparse import ArgumentParser
from datetime import datetime
from os import system
from sys import argv
from time import sleep
from pathlib import Path


DIR = Path(__file__).parent
TIME_DELAY = 5


class main:
    def __init__(self) -> None:
        print(' Cronjob started '.center(50, '-'))
        parser = ArgumentParser()
        parser.add_argument(
            'job',
            help = 'Specify job to execute',
            choices = ['full-load', 'synonyms-load', 'refresh-event']
        )
        self.job = parser.parse_args().job
        self.start_job()
    
    def start_job(self):
        print(f'Job: {self.job}')
        print(f'-'*50)
        system(f'python -u {DIR / "CPAGE" / self.job}.py {TIME_DELAY}')


if __name__ == '__main__':
    main()
    