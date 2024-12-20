from datetime import datetime
from os import listdir
from pathlib import Path
from time import sleep
from vars import *


def main():
    print('Waiting for previous job to complete')
    while 'full_load_complete' not in listdir('/mnt'):
        sleep(SLEEP_DELAY)
    start = datetime.now()
    print(f'Job started at   : {start}')
    sleep(TIME_DELAY)
    stop = datetime.now()
    print(f'Job completed at : {stop}')
    print('Sent a trigger for next job: ["refresh_event"]')
    Path('/mnt/synonyms_load_complete').touch()


if __name__ == '__main__':
    main()