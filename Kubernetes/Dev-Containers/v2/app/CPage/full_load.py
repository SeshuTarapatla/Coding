from datetime import datetime
from os import listdir
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
    print('Waiting for other jobs to complete before exiting')
    while 'synonyms_load_complete' not in listdir('/mnt'):
        sleep(SLEEP_DELAY)
    print(' Job: synonyms_load -> Complete')
    while 'refresh_event_complete' not in listdir('/mnt'):
        sleep(SLEEP_DELAY)
    print(' Job: refresh_event -> Complete')
    print('---------------- Cronjob complete ----------------')


if __name__ == '__main__':
    main()