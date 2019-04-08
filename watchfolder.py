import time

from configparser import ConfigParser
from watchdog.observers import  Observer

import logging
import json
from scripts.processor import *


class Watcher:


    parser = ConfigParser()
    parser.read(os.path.join('data', 'config.ini'))

    project_dirs = json.loads(parser.get('directories', 'project_dirs'))

    DIRECTORY_TO_WATCH = project_dirs
    print('Watchfolder started...')
    print('Running on these directories:')
    for i in range(len(project_dirs)):
        print(project_dirs[i])

    def __init__(self):

        self.observer = Observer()

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

    format = '%(levelname)s\t%(asctime)s\t%(message)s'
    datefmt = '%Y-%m-%d %I:%M:%S'
    filename = os.path.join('data', 'providers.log')
    logging.basicConfig(handlers=[logging.FileHandler(filename, 'a', 'utf-8')],
                        format=format,
                        level=logging.INFO,
                        datefmt=datefmt)

    w = Watcher()
    w.run()
