from logging.handlers import TimedRotatingFileHandler

from watchdog.observers import Observer

from scripts.processor import *


class Watcher:
    parser = ConfigParser()
    parser.read(os.path.join('data', 'config.ini'), encoding='utf8')
    # Load config data and store list as as global variable.
    # The loads method allows for the use of whitespace in the config file
    project_dirs = json.loads(parser.get('directories', 'project_dirs'))

    DIRECTORY_TO_WATCH = project_dirs
    print('Watchfolder started...')
    print('Running on these directories:')
    for directory in project_dirs:
        print(directory)

    def __init__(self):

        self.observer = Observer()

    def run(self):

        # Define file extensions to be considered for events
        patt = ['*.sdlrpx', '*.wsxz', '*.sdlxliff']
        event_handler = Processor(patterns=patt)

        # Loop over watchfolder directories to schedule observer threads
        for directory in self.DIRECTORY_TO_WATCH:
            self.observer.schedule(event_handler, directory, recursive=True)

        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()

        self.observer.join()


if __name__ == '__main__':
    fmt = '%(levelname)s\t%(asctime)s\t%(message)s'
    datefmt = '%Y-%m-%d %I:%M:%S'
    filename = os.path.join('data', 'providers.log')
    handler = TimedRotatingFileHandler(filename, encoding='utf-8', when='midnight', interval=1)

    logging.basicConfig(handlers=[handler],
                        format=fmt,
                        level=logging.INFO,
                        datefmt=datefmt)
    logging.info('Process started by {}'.format(os.path.expanduser("~")))

    w = Watcher()
    w.run()
