from datetime import datetime
from os import listdir
from pathlib import Path
from sys import argv
from time import sleep


def main():
    print('Waiting for full-load stage to complete')
    while 'full-load-complete' not in listdir('/mnt'):
        sleep(1)
    print(f'Execution started at  : {datetime.now()}')
    sleep(int(argv[1]))
    print(f'Execution completed at: {datetime.now()}')
    Path('/mnt/synonyms-load-complete').touch()
    print('Triggered next stage: "synonyms-load"')


if __name__ == '__main__':
    main()
    