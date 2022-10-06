import configparser
import getopt
import sys
import time

import config
import logo
import pdf_processor
from utility import wise_monkey_says, load_shape_files

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

        conf = configparser.ConfigParser()
        read_files = conf.read(config_file)
        if len(read_files) == 0:
            wise_monkey_says(f"Configuration file {config_file} can't be found")
            sys.exit(1)
        config.config_dict = {s: dict(conf.items(s)) for s in conf.sections()}

        if 'json_store_location' in config.config_dict['Base Information'].keys():
            config.json_store_location = config.config_dict['Base Information']['json_store_location']
            load_shape_files()
        else:
            wise_monkey_says('You forgot to tell me where the json files can be found')
            wise_monkey_says('if you set the json_store in the configuration file we can try again')
            sys.exit(1)

        config.product_shape = config.config_dict['Product Information']['product_shape']
        config.product_shape_lower = config.product_shape.lower()
        if config.product_shape_lower == 'regular':
            config.is_regular_product = True
            config.regular_product = config.config_dict['Product Information']['regular_product']
            config.regular_product_lower = config.regular_product.lower()
        else:
            config.is_regular_product = False
            wise_monkey_says(f'Looks like we will be working on the {config.product_shape} product')

        pdf_processor.process()
        config.end_process_time = time.perf_counter()
        elapsed = config.end_process_time - config.start_process_time
        elapsed_format = '{:.2f}'.format(elapsed)
        wise_monkey_says(f'For Reference the process took {elapsed_format} seconds')


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(help_str)
        sys.exit()
    main(sys.argv[1:])
