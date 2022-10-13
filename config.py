""" Contains Global variables

Information that should be treated as global in nature are added here.
Importing the module will bring the variables into scope of other
modules.
"""
import configparser
import sys

from constants import ProcessType, GeneralConstants
from utility import wise_monkey_says_oops

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
input_xmind_document = ''
start_process_time = ''
end_process_time = ''
language = 'en'
language_name = 'English'
language_file = 'en_core_web_md'
system_setting_data = []
process_type: ProcessType


def read_configuration(configuration_file_path):
    """Read the configuration file

    The configuration file is read from the supplied location and the contents
    assigned to config_dict.
    """
    conf = configparser.ConfigParser()
    read_files = conf.read(configuration_file_path)
    if len(read_files) == 0:
        wise_monkey_says_oops(f"Configuration file {configuration_file_path} can't be found")
        sys.exit(1)
    global config_dict
    config_dict = {s: dict(conf.items(s)) for s in conf.sections()}


def set_input_files():
    """Set the pdf or xmind input file locations

    The input file locations are checked and assigned, the input is
    validated to ensure there is only one input file.
    """
    global config_dict
    global input_document
    global input_xmind_document
    global process_type
    process_type = ProcessType.to_xmind
    if 'input_xmind_document' in config_dict[GeneralConstants.base_information.value].keys():
        input_xmind_document = config_dict[GeneralConstants.base_information.value]['input_xmind_document']
        process_type = ProcessType.from_xmind

    if len(input_document) > 0 and len(input_xmind_document) > 0:
        wise_monkey_says_oops(f'You are trying to be greedy, I can only allow one input file either pdf or xmind')
        sys.exit(1)
