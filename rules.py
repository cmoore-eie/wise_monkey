import json
import os

import config


def build_rules(rule_type, matcher):
    """Builds the matcher rules from the rule definitions in the json file rules_...

    Rules stored in the json file are extracted if the file exists where the
    configuration is set to look. As the json representation of the rules
    need to be modified to conform with how the rules should look to be
    added to the matcher.
    """
    file_key = f'{rule_type} rules'
    file_path = f'{config.json_store_location}{config.json_store_files[file_key]}'
    if os.path.exists(file_path):
        with open(file_path) as json_file:
            data = json.load(json_file)
            for rule_name in data.keys():
                pattern_json = data[rule_name]
                pattern = []
                for pattern_list in pattern_json:
                    item_body = []
                    for pattern_item in pattern_list:
                        item_body_part = dict()
                        for key in pattern_item.keys():
                            if key == 'IS_PUNCT':
                                item_body_part[key] = True
                            elif key == 'IS_TITLE':
                                item_body_part[key] = True
                            else:
                                item_body_part[key] = pattern_item[key]
                        item_body.append(item_body_part)
                    pattern.append(item_body)
                matcher.add(rule_name.upper(), pattern, on_match=None)


def build_matcher_rules(matcher):
    build_rules('other', matcher)
    build_rules(config.product_shape_lower, matcher)
