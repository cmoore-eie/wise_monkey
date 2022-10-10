import json
import sys
from json import JSONDecodeError
import config
from utility import wise_monkey_says_oops


def fetch_languages() -> dict:
    languages = dict()
    if 'Languages' in config.system_setting_data.keys():
        for item in config.system_setting_data['Languages']:
            languages[item['CODE']] = item['NAME']
    return languages


def fetch_language_codes() -> list:
    language_codes = []
    if 'Languages' in config.system_setting_data.keys():
        for item in config.system_setting_data['Languages']:
            language_codes.append(item['CODE'])
    return language_codes


def fetch_languages_files() -> dict:
    languages = dict()
    if 'Languages' in config.system_setting_data.keys():
        for item in config.system_setting_data['Language Files']:
            languages[item['CODE']] = item['NAME']
    return languages


def fetch_language_file_codes() -> list:
    language_codes = []
    if 'Languages' in config.system_setting_data.keys():
        for item in config.system_setting_data['Language Files']:
            language_codes.append(item['CODE'])
    return language_codes


def read_system_settings():
    system_file = config.json_store_location + 'system_settings.json'
    try:
        with open(system_file) as json_file:
            config.system_setting_data = json.load(json_file)
    except JSONDecodeError:
        wise_monkey_says_oops(f"The json file system_settings.json can't be processed")
        sys.exit(1)
