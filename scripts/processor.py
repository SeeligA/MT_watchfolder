import re
import os.path
import zipfile

from configparser import ConfigParser
from watchdog.events import PatternMatchingEventHandler
from collections import defaultdict



class Processor(PatternMatchingEventHandler):


    @staticmethod
    def on_created(event):

        parser = ConfigParser()
        parser.read(os.path.join('data', 'config.ini'), encoding = 'utf-8')

        delivery_dir = parser.get('directories', 'delivery_dir').split(',')
        blacklisted = parser.get('mt providers', 'blacklist').split(',')


        for folder in delivery_dir:
            if folder in event.src_path:
                providers = Processor.unzip_working_files(event.src_path)

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


        providers = dict()


        with zipfile.ZipFile(filepath, 'r') as return_package:

            for fp in return_package.namelist():

                if fp.endswith('.sdlxliff'):

                    with return_package.open(fp) as working_file:
                        providers[fp] = Processor.get_providers(working_file.read())


        return providers


    def check_against_blacklist(providers, blacklist):

        mt_providers = {}


        for file, values in providers.items():
            matches = []

            for mt_provider in blacklist:

                for origin in values.keys():
                    # encode string to
                    if mt_provider.encode('utf-8') in providers[file][origin]:
                        matches.append(mt_provider)

            if len(matches) > 0:
                mt_providers[file] = matches

        return mt_providers


    def print_warning(file_path, mt_providers):

        with open(os.path.join(file_path, "MT WARNING.txt"), "a") as f:

            f.write('MT found in return package.\n')
            for k, v in mt_providers.items():
                f.write(str('Affected file: {}\nMT provider(s): {}\n'.format(k, v)))


    def load_blacklist():

        providers = parser.get('mt providers', 'blacklist').split(',')

        return providers



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

            count[j] += 1
            providers[i][j] = count[j]

        return providers
