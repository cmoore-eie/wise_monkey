""" Contains Global variables

Information that should be treated as global in nature are added here.
Importing the module will bring the variables into scope of other
modules.
"""
import configparser
import sys

from utility import wise_monkey_says

config_dict = dict()
shape_dict = dict()
product_shape = ''
product_shape_lower = ''
regular_product = ''
regular_product_lower = ''
is_regular_product = False
json_store_location = ''
json_store_files = []
matcher_phrases = []
output_file_location = ''
input_document = ''
start_process_time = ''
end_process_time = ''
language = 'en'
language_name = 'English'
language_file = 'en_core_web_md'
system_setting_data = []


def read_configuration(configuration_file_path):
    conf = configparser.ConfigParser()
    read_files = conf.read(configuration_file_path)
    if len(read_files) == 0:
        wise_monkey_says(f"Configuration file {configuration_file_path} can't be found")
        sys.exit(1)
    global config_dict
    config_dict = {s: dict(conf.items(s)) for s in conf.sections()}
