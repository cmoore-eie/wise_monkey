import json
import os
import sys
from json import JSONDecodeError

import config
import utility
from constants import JSON_KEYS, MARKERS


def apply_shape(line, coverages=None):
    for json_risk_object in config.shape_dict[JSON_KEYS['risk_objects']]:
        risk_object = line.addSubTopic()
        risk_object.setTitle(json_risk_object['NAME'])
        risk_object.addMarker(MARKERS[json_risk_object['TYPE']])
        if 'LABEL' in json_risk_object.keys():
            risk_object.addLabel(json_risk_object['LABEL'])

        risk_object_notes = risk_object.addSubTopic()
        risk_object_notes.setTitle("Notes")
        risk_object_notes.addMarker(MARKERS['info'])

        risk_object_attribute = risk_object.addSubTopic()
        risk_object_attribute.setTitle("Attributes")

        if JSON_KEYS['attributes'] in json_risk_object.keys():
            utility.add_xmind_attributes(risk_object_attribute, json_risk_object)

        risk_object_coverage = risk_object.addSubTopic()
        risk_object_coverage.setTitle("Coverages")

        risk_object_exclusions = risk_object.addSubTopic()
        risk_object_exclusions.setTitle("Exclusions")
        risk_object_exclusions_category = risk_object_exclusions.addSubTopic()
        risk_object_exclusions_category.setTitle("Standard Exclusions")
        risk_object_exclusions_category.addMarker(MARKERS['clause_category'])

        risk_object_conditions = risk_object.addSubTopic()
        risk_object_conditions.setTitle("Conditions")
        risk_object_conditions_category = risk_object_conditions.addSubTopic()
        risk_object_conditions_category.setTitle("Standard Conditions")
        risk_object_conditions_category.addMarker(MARKERS['clause_category'])

        if JSON_KEYS['coverages'] in json_risk_object.keys():
            coverages = json_risk_object[JSON_KEYS['coverages']]

        utility.add_xmind_coverages(coverages, json_risk_object, risk_object_coverage)


def shape_to_dict(shape):
    if len(config.shape_dict.keys()) > 0:
        return config.shape_dict

    if config.is_regular_product:
        test_product_shape = config.regular_product_lower
    else:
        test_product_shape = config.product_shape_lower

    if test_product_shape in config.json_store_files.keys():
        file_path = config.json_store_location + config.json_store_files[test_product_shape]
        if os.path.exists(file_path):
            with open(file_path) as json_file:
                try:
                    config.shape_dict = json.load(json_file)
                    return config.shape_dict
                except JSONDecodeError:
                    utility.wise_monkey_says_oops(f' The json file {file_path} is not valid.')
                    sys.exit(1)
        else:
            utility.wise_monkey_says_oops(
                f'Missing shape file from the json store located at {config.json_store_location}')
            utility.wise_monkey_says_oops(f'Please add the file {config.json_store_files[config.product_shape_lower]}')
            sys.exit(1)
    else:
        utility.wise_monkey_says_oops(f'There is no definition for Shape {shape}')
        utility.wise_monkey_says_oops(f'Proceeding with no product shape')
        return {'Attributes': []}


def dropdown_to_dict(dropdown_name):
    shape_file = config.json_store_location + config.json_store_files['dropdown']
    with open(shape_file) as json_file:
        data = json.load(json_file)
        if dropdown_name in data.keys():
            return data[dropdown_name]
        else:
            return []


def is_related(json_object, child):
    """Identifies if the attribute is a child in the relationship

    if the child is part of a defined relationship it will be created when the dropdown values of the parent are
    processed, otherwise it needs to be ignored.

    :parameter shape_dict the product shape dictionary
    :parameter child the attribute to search for
    :return bool False if the child is not related otherwise it will return True
    """
    if JSON_KEYS['related'] not in json_object.keys():
        return False
    related = json_object[JSON_KEYS['related']]
    for relationship in related:
        if relationship['CHILD'] == child:
            return True
    return False
