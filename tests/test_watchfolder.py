import pytest
from scripts.processor import *


def test_load_config():

    fp = os.path.join('data', 'config.ini')
    fp = os.path.join('..', fp)
    assert os.path.exists(fp)

    delivery_dir, blacklisted = Processor.load_config(fp)

    assert isinstance(delivery_dir, list) & len(delivery_dir) > 0



def test_unzip_working_files():

    assert isinstance(Processor.unzip_working_files("watchfolder_test.wsxz"), dict)


def test_get_providers():
    files = {1: "ru-RU.sdlxliff", 2: "zh-CN.sdlxliff"}

    providers = dict()
    for i in files:
        with open(files[i], "rb") as working_file:
            providers[i] = Processor.get_providers(working_file.read())
            assert isinstance(providers[i], dict)

            keys = []
            values = []
            for k, v in providers[i].items():
                assert isinstance(k, str)
                assert isinstance(v, dict)

    return providers

def test_log_providers():

    providers = test_get_providers()
    assert Processor.log_providers(providers) == None
