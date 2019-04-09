import re
import os.path
import zipfile
import time

import json
import logging
from configparser import ConfigParser
from watchdog.events import PatternMatchingEventHandler
from collections import defaultdict



class Processor(PatternMatchingEventHandler):
    '''
    -> load_config() -> on_created() -> unzip_working_files() -> get_providers()
    -> log_providers() -> check_against_blacklist() -> print_warning()
    '''


    @staticmethod
    def on_created(event):

        delivery_dir, blacklisted = Processor.load_config(os.path.join('data', 'config.ini'))

        if [True for folder in delivery_dir if folder not in event.src_path]:
            return None

        print('\nNew deliverable found: {}. Checking for providers...'.format(event.src_path))

        timeout = 0
        while timeout < 10:
            try:
                providers = Processor.unzip_working_files(event.src_path)
                timeout = 10

            except FileNotFoundError:
                try:
                    providers = Processor.unzip_working_files(os.path.join(event.src_path, 'wsxz'))
                    timeout = 10

                except FileNotFoundError:
                    time.sleep(4)

            else:
                timeout += 1

        mt_providers = Processor.check_against_blacklist(providers, blacklisted)

        if len(mt_providers) > 0:
            Processor.print_warning(os.path.dirname(event.src_path), mt_providers)


    @classmethod
    def unzip_working_files(cls, filepath):

        '''
        Open return package and collect translation providers from *.SDLXLIFF working files

        Arguments:
        filepath -- return package flagged by observer instance

        Returns
        providers -- nested dictionary containing providers + counts per *.SDLXLIFF working file
        '''

        time.sleep(1)

        providers = dict()

        if filepath.endswith('.sdlxliff'):

            regex = re.compile(r'[^\\]+?\.sdlxliff$')
            fp = regex.search(filepath).group()

            with open(filepath, 'rb') as working_file:
                providers[fp] = Processor.get_providers(working_file.read())

        else:
            timeout = 0
            while timeout < 10:

                try:
                    with zipfile.ZipFile(filepath, 'r') as return_package:

                        for fp in return_package.namelist():

                            if fp.endswith('.sdlxliff'):

                                with return_package.open(fp) as working_file:
                                    providers[fp] = Processor.get_providers(working_file.read())
                    counter = 10

                except PermissionError:
                    time.sleep(2)
                else:
                    timeout +=1

        Processor.log_providers(providers)

        return providers

    def load_config(fp):
        parser = ConfigParser()
        parser.read(fp)

        delivery_dir = json.loads(parser.get('directories', 'delivery_dir'))
        blacklisted = json.loads(parser.get('mt providers', 'blacklist'))

        return(delivery_dir, blacklisted)


    def check_against_blacklist(providers, blacklist):

        mt_providers = {}


        for file, values in providers.items():
            matches = []

            for mt_provider in blacklist:

                for origin in values.keys():

                    if mt_provider in providers[file][origin]:
                        matches.append(mt_provider)

            if len(matches) > 0:
                mt_providers[file] = matches

        return mt_providers


    def print_warning(file_path, mt_providers):

        print('\nMT providers found. Check {} for details'.format('\\'.join((file_path, 'MT WARNING.txt'))))
        with open(os.path.join(file_path, "MT WARNING.txt"), "a") as f:

            f.write('MT providers found.\n')
            for k, v in mt_providers.items():
                f.write(str('Affected file: {}\nMT provider(s): {}\n'.format(k, v)))

                logging.warning('{}\t{}'.format(k, v))



    def log_providers(providers):

        for fp, details in providers.items():

            for k, v in details.items():
                # Add filter for auto-propagated TM matches
                if k != "auto-propagated":

                    for system, count in v.items():

                        logging.info('{}\t{}\t{}'.format(fp, system, count))

    def get_providers(working_file):
        '''
        Collect translation providers from translated segments

        Arguments:
        working_file -- in XML format

        Returns:
        providers -- dictionary taking the format providers[origin][origin-system] = count
        '''
        regex = re.compile(b'origin="([^"]+)" origin-system="([^"]+)"')

        origins = regex.findall(working_file)


        providers = defaultdict(dict)
        count = defaultdict(int)

        for i, j in origins:
            i = i.decode('utf8')
            j = j.decode('utf8')
            count[j] += 1
            providers[i][j] = count[j]

        return providers
