import json
import logging
import os.path
import re
import time
import zipfile
from collections import defaultdict
from configparser import ConfigParser

from watchdog.events import PatternMatchingEventHandler


class Processor(PatternMatchingEventHandler):
    """
    -> load_config() -> on_created() -> read_working_file()/read_return_package() -> get_providers()
    -> log_providers() -> check_against_blacklist() -> print_warning()
    """

    def on_created(self, event):
        self.path = event.src_path

        delivery_dir, blacklisted = self.load_config(os.path.join('data', 'config.ini'))
        # Check file path against delivery_dir filter and end if no match was found
        if len([True for folder in delivery_dir if folder not in event.src_path]) == len(delivery_dir) and len(
                delivery_dir) != 0:
            return None

        print('\nNew deliverable found: {}. Checking for providers...'.format(self.path), end='')

        if self.path.endswith('.sdlxliff'):
            providers = self.read_working_file()

        else:
            providers = self.read_return_package()
            if providers is None:
                return print(' Unable to access file. Abort process.')

        mt_providers = self.check_against_blacklist(providers, blacklisted)

        if len(mt_providers) > 0:
            print_warning(os.path.dirname(self.path), mt_providers)
        else:
            print(' Check complete: All good.')

        self.log_providers(providers)

    def read_return_package(self):
        """
        Open return package and collect translation providers from *.SDLXLIFF working files

        Returns
        providers -- nested dictionary containing providers + counts per *.SDLXLIFF working file
        """

        time.sleep(1)

        providers = dict()

        timeout = 0
        while timeout < 10:
            print('.', end='')

            try:
                with zipfile.ZipFile(self.path, 'r') as return_package:

                    for fp in return_package.namelist():

                        if fp.endswith('.sdlxliff'):
                            with return_package.open(fp) as f:
                                providers[fp] = get_providers(f.read())

                    return providers

            except FileNotFoundError:
                return None

            # Allow for extra time in case creating the return package takes longer
            except PermissionError:
                time.sleep(2)
                if timeout == 10:
                    return None

            finally:
                timeout += 1

    def read_working_file(self):
        """
        Collect translation providers from a single *.SDLXLIFF working file

        Arguments:
        filepath -- return package flagged by observer instance

        Returns
        providers -- dictionary containing providers + counts for *.SDLXLIFF working file
        """
        time.sleep(1)
        providers = dict()

        with open(self.path, 'rb') as f:
            providers[os.path.basename(self.path)] = get_providers(f.read())

        return providers

    @staticmethod
    def load_config(fp):
        parser = ConfigParser()
        parser.read(fp, encoding='utf8')

        delivery_dir = json.loads(parser.get('directories', 'delivery_dir'))
        blacklisted = json.loads(parser.get('mt providers', 'blacklist'))

        return delivery_dir, blacklisted

    @staticmethod
    def check_against_blacklist(providers, blacklist):
        """
        Check provider information for blacklisted entries
        Arguments:
        provider -- dictionary taking the format providers[origin][origin-system] = count
        blacklist -- list of blacklisted provider names

        Returns
        mt_providers -- dictionary with file names as keys and matched providers as values
        """
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

    def log_providers(self, providers):
        """

        """
        logging.info('Deliverable: {}'.format(self.path))

        for fp, details in providers.items():

            for k, v in details.items():
                # Add filter for auto-propagated TM matches
                if k != "auto-propagated":

                    for system, count in v.items():
                        logging.info('{}\t{}\t{}'.format(fp, system, count))


def get_providers(working_file):
    """
    Collect translation providers from translated segments

    Arguments:
    working_file -- in XML format

    Returns:
    providers -- dictionary taking the format providers[origin][origin-system] = count
    """
    regex = re.compile(b'origin="([^"]+)" origin-system="([^"]+)"')
    # return a list of tuples ('origin', 'origin_system')
    origins = regex.findall(working_file)

    providers = defaultdict(dict)
    count = defaultdict()

    for i, j in origins:
        i = i.decode('utf8')
        j = j.decode('utf8')
        count[j] += 1
        providers[i][j] = count[j]

        return providers


def print_warning(dir_path, mt_providers):
    print('\nMT providers found. Check {} for details'.format('\\'.join((dir_path, 'MT WARNING.txt'))))
    with open(os.path.join(dir_path, "MT WARNING.txt"), "a", encoding='utf8') as f:
        f.write('MT providers found.\n')
        for k, v in mt_providers.items():
            f.write(str('See file: {}\nMT provider(s): {}\n'.format(k, v)))

            logging.warning('{}\t{}'.format(k, v))
