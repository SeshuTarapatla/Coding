from argparse import ArgumentParser
from os import system
system('clear')


class main:
    def __init__(self) -> None:
        parser = ArgumentParser()
        parser.add_argument(
            'job', help=['Specify the job to run'], choices=['full_load', 'synonyms_load', 'refresh_event']
        )
        self.job = parser.parse_args().job
        self.initiate_job()
    
    def initiate_job(self) -> None:
        print(f'---------------- Cronjob started -----------------')
        print(f' Job: {self.job}')
        print(f'--------------------------------------------------')
        system(f'python -u CPage/{self.job}.py')


if __name__ == '__main__':
    main()