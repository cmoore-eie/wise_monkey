import getopt
import sys
import time
import config
import constants
import logo
import pdf_processor
import glob
import xmind_2_json_shape
from constants import GeneralConstants
from system_settings import read_system_settings, fetch_language_codes, fetch_language_file_codes
from utility import wise_monkey_says, load_shape_files, wise_monkey_says_oops

process_errors = dict()
help_str = '''

Please supply the arguments for -c
        -c, --config - path to the json configuration file
        -h, --help - displays this text

        '''


def main(argv):
    config.start_process_time = time.perf_counter()
    print(logo.logo_image)
    print("")
    config_file: str = ''

    try:
        opts, args = getopt.getopt(argv, 'c:', ['help', 'config ='])
        for opt, arg in opts:
            if opt in ['-c', '--config']:
                config_file = arg.strip()
            elif opt in ['-h', '--help']:
                print(help_str)
                sys.exit()
            else:
                sys.exit()
    except getopt.GetoptError:
        print(help_str)
        sys.exit(2)

    if config_file == '':
        process_errors[len(process_errors) +
                       1] = "-c (--config) missing and is required"
        sys.exit(1)

    if len(process_errors) > 0:
        print("")
        print("Missing Parameter Information")
        print("=============================")
        for error_item in process_errors:
            print(f"({error_item}) : {process_errors[error_item]}")
    else:
        config.read_configuration(config_file)
        config.set_input_files()

        set_json_store()
        fetch_system_settings()
        if config.process_type == constants.ProcessType.to_xmind:
            process_to_xmind()
        if config.process_type == constants.ProcessType.from_xmind:
            process_from_xmind()
        if config.process_type == constants.ProcessType.from_xmind_bulk:
            process_from_xmind_bulk()


def process_from_xmind():
    xmind_2_json_shape.process_from_xmind(config.input_xmind_document)
    config.end_process_time = time.perf_counter()
    elapsed = config.end_process_time - config.start_process_time
    elapsed_format = '{:.2f}'.format(elapsed)
    wise_monkey_says(f'For Reference the process took {elapsed_format} seconds')


def process_from_xmind_bulk():
    file_search = config.input_xmind_document + "/*.xmind"
    file_list = glob.glob(file_search)
    for file in file_list:
        wise_monkey_says(f'I am typeing as fast as I can to generate json from {file} ')
        xmind_2_json_shape.process_from_xmind(file)
    config.end_process_time = time.perf_counter()
    elapsed = config.end_process_time - config.start_process_time
    elapsed_format = '{:.2f}'.format(elapsed)
    wise_monkey_says(f'For Reference the process took {elapsed_format} seconds')


def process_to_xmind():
    set_language()
    set_language_file()
    set_product_shape()

    pdf_processor.process()
    config.end_process_time = time.perf_counter()
    elapsed = config.end_process_time - config.start_process_time
    elapsed_format = '{:.2f}'.format(elapsed)
    wise_monkey_says(f'For Reference the process took {elapsed_format} seconds')


def fetch_system_settings():
    read_system_settings()


def set_language():
    """ Set the language code

    Extracts the language value from the configuration file, if there is no language
    specified the default of English (en) will be set
    """
    config.language = 'en'
    message_process = True
    if GeneralConstants.language_information.value in config.config_dict.keys():
        if 'language' in config.config_dict[GeneralConstants.language_information.value].keys():
            supplied_language = config.config_dict[GeneralConstants.language_information.value]['language']
            if len(supplied_language) > 0:
                if supplied_language not in fetch_language_codes():
                    wise_monkey_says_oops(f"Currently I am not supporting a language with the code {supplied_language}")
                    wise_monkey_says_oops(f'I will do my best to learn this language for our next visit')
                    sys.exit(1)
                message_process = False
                config.language = supplied_language
            else:
                message_process = True

    if message_process:
        wise_monkey_says_oops(f"As you didn't supply a language English (en) will be used")
        wise_monkey_says_oops(f"Add the language parameter to the ini file if you want a different language")


def set_language_file():
    """ Set the language code

    Extracts the language value from the configuration file, if there is no language
    specified the default of English (en) will be set
    """
    config.language_file = 'en_core_web_md'
    message_process = True
    if GeneralConstants.language_information.value in config.config_dict.keys():
        if 'language_file' in config.config_dict[GeneralConstants.language_information.value].keys():
            supplied_language_file = config.config_dict[GeneralConstants.language_information.value]['language_file']
            if len(supplied_language_file) > 0:
                if supplied_language_file not in fetch_language_file_codes():
                    wise_monkey_says_oops(f"I currently don't handle {supplied_language_file} language file")
                    wise_monkey_says_oops(f'I will explore the option of making use of this in the future')
                    sys.exit(1)
                message_process = False
                config.language_file = supplied_language_file
            else:
                message_process = True

    if message_process:
        wise_monkey_says(f"As you didn't supply a language file 'en_core_web_md' will be used")
        wise_monkey_says(f"Add the language_file parameter to the ini file that corresponds to the language set")


def set_json_store():
    """Extract the json_store configuration

    Extracts the location of the json store processes the
    json_store.json file to get a dictionary to use
    """
    if 'json_store_location' in config.config_dict[GeneralConstants.base_information.value].keys():
        config.json_store_location = config.config_dict[GeneralConstants.base_information.value]['json_store_location']
        load_shape_files()
    else:
        wise_monkey_says('You forgot to tell me where the json files can be found')
        wise_monkey_says('if you set the json_store in the configuration file we can try again')
        sys.exit(1)


def set_product_shape():
    """Sets the product shape config parameter

    Sets the product shape and product shape lower config values, if the product is
    defined as regular the regular product and regular product lower are set
    """
    config.product_shape = config.config_dict[GeneralConstants.product_information.value]['product_shape']
    config.product_shape_lower = config.product_shape.lower()
    if config.product_shape_lower == 'regular':
        config.is_regular_product = True
        config.regular_product = config.config_dict[GeneralConstants.product_information.value]['regular_product']
        config.regular_product_lower = config.regular_product.lower()
    else:
        config.is_regular_product = False
        wise_monkey_says(f'Looks like we will be working on the {config.product_shape} product')


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(help_str)
        sys.exit()
    main(sys.argv[1:])
