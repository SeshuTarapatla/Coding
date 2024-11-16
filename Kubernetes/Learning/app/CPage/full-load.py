from datetime import datetime
from pathlib import Path
from sys import argv
from time import sleep


def main():
    print(f'Execution started at  : {datetime.now()}')
    sleep(int(argv[1]))
    print(f'Execution completed at: {datetime.now()}')
    Path('/mnt/full-load-complete').touch()
    print('Triggered next stage: "synonyms-load"')


if __name__ == '__main__':
    main()
    