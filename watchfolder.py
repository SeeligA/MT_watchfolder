import time

from configparser import ConfigParser
from watchdog.observers import  polling

from scripts.processor import *


class Watcher:


    parser = ConfigParser()
    parser.read(os.path.join('data', 'config.ini'), encoding = 'utf-8')


    project_dirs = parser.get('directories', 'project_dirs').split(',')

    DIRECTORY_TO_WATCH = project_dirs
    print('Watchfolder started...')
    print('Running on these directories:')
    for i in range(len(project_dirs)):
        print(project_dirs[i])

    def __init__(self):


        # OS-independent: slow
        self.observer = polling.PollingObserver()

    def run(self):

        # Define file extensions to be considered for events
        patt = ['*.sdlrpx', '*.wsxz']
        event_handler = Processor(patterns=patt)

        # Loop over watchfolder directories to schedule observer threads
        for i in range(len(self.DIRECTORY_TO_WATCH)):
            self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH[i], recursive=True)

        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()

        self.observer.join()



if __name__ == '__main__':
    w = Watcher()
    w.run()
