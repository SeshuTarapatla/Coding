from datetime import datetime
from os import listdir
from sys import argv
from time import sleep


def main():
    print('Waiting for synonyms-load stage to complete')
    while 'synonyms-load-complete' not in listdir('/mnt'):
        sleep(1)
    print(f'Execution started at  : {datetime.now()}')
    sleep(int(argv[1]))
    print(f'Execution completed at: {datetime.now()}')


if __name__ == '__main__':
    main()
    