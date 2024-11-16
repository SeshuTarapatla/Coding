from datetime import datetime
from pathlib import Path
from time import sleep
from vars import *


def main():
    start = datetime.now()
    print(f'Job started at   : {start}')
    sleep(TIME_DELAY)
    stop = datetime.now()
    print(f'Job completed at : {stop}')
    print('Sent a trigger for next job: ["synonyms_load"]')
    Path('/mnt/full_load_complete').touch()


if __name__ == '__main__':
    main()