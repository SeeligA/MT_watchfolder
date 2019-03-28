# MT_watchfolder

MT_watchfolder is a Python script that monitors your SDL Trados Studio deliverables for TM/MT provider information. Run it on your file directory to log provider details. Add provider information to your blacklist and raise a warning if a criteria has been met.

## Requirements

MT_watchfolder requires [watchdog](https://pypi.org/project/watchdog/).
```
pip install watchdog
```
Check the [requirements](https://github.com/SeeligA/MT_watchfolder/blob/master/docs/requirements.txt) for more details.

## Configuration
* Open the config.ini file
* In the _directories_ section:
  * Add at least one path to specify a project directory
  * Optional: Add a filter string to filter for paths containing the string
* in the _blacklist_ section: This is where you specify names of forbidden providers

## Running the script
```
python watchfolder.py
```
This will start an Observer instance. Any registered event will be passed to the Processor for  running the relevant checks.
* MT providers will be logged under **data/providers.log**.
* If a blacklisted provider has been found, a **WARNING.txt** file will be created in the delivery folder

## Optional: Testing
In order to run the script test_watchfolder.py successfully you will need to:
* Install [pytest](https://docs.pytest.org/en/latest/) using pip or conda:
```
pip install pytest
```

* Install the project package by installing setup.py in the root directory:
```
pip install -e .
```

## Questions
Feel free to drop me a line in case of any questions.

![flow chart](https://github.com/SeeligA/MT_watchfolder/blob/master/docs/MT_watchfolder.png)
