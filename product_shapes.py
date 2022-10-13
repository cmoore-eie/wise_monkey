import json
import os
import sys
from json import JSONDecodeError

import config
import utility
from constants import JsonKeys, Markers


def apply_shape(line, coverages=None):
    """Applies the information to the mind map for each risk object

    Loops over the risk objects defined in the shape file adding it,
    attributes and coverages. If there has been an import file to
    process then coverages from the shape will be ignored in favour of
    the coverages extracted.
    """
    for json_risk_object in config.shape_dict[JsonKeys.risk_objects.value]:
        risk_object = line.addSubTopic()
        risk_object.setTitle(json_risk_object[JsonKeys.name.value])
        risk_object.addMarker(Markers[json_risk_object[JsonKeys.type.value]].value)
        if JsonKeys.label.value in json_risk_object.keys():
            risk_object.addLabel(json_risk_object[JsonKeys.label.value])

        risk_object_notes = risk_object.addSubTopic()
        risk_object_notes.setTitle("Notes")
        risk_object_notes.addMarker(Markers.info.value)

        risk_object_attribute = risk_object.addSubTopic()
        risk_object_attribute.setTitle("Attributes")

        if JsonKeys.attributes.value in json_risk_object.keys():
            utility.add_xmind_attributes(risk_object_attribute, json_risk_object)

        risk_object_coverage = risk_object.addSubTopic()
        risk_object_coverage.setTitle("Coverages")

        risk_object_exclusions = risk_object.addSubTopic()
        risk_object_exclusions.setTitle("Exclusions")
        risk_object_exclusions_category = risk_object_exclusions.addSubTopic()
        risk_object_exclusions_category.setTitle("Standard Exclusions")
        risk_object_exclusions_category.addMarker(Markers.clause_category.value)

        risk_object_conditions = risk_object.addSubTopic()
        risk_object_conditions.setTitle("Conditions")
        risk_object_conditions_category = risk_object_conditions.addSubTopic()
        risk_object_conditions_category.setTitle("Standard Conditions")
        risk_object_conditions_category.addMarker(Markers.clause_category.value)

        if JsonKeys.coverages.value in json_risk_object.keys() and (coverages is None or len(coverages) == 0):
            coverages = json_risk_object[JsonKeys.coverages.value]

        utility.add_xmind_coverages(coverages, json_risk_object, risk_object_coverage)


def extract_shape(shape) -> list:
    if len(config.shape_dict.keys()) > 0:
        return config.shape_dict

    if config.is_regular_product:
        test_product_shape = config.regular_product_lower
    else:
        test_product_shape = config.product_shape_lower

    store_item = utility.extract_store_file(test_product_shape)

    if store_item is not None:
        file_path = config.json_store_location + store_item
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
        return []


def dropdown_to_dict(dropdown_name: str) -> list:
    """Converts the dropdown json definitions for a named set to a list

    The json file is read and converted to a dictionary, the key
    corresponding to the dropdown name is extracted and returned else
    an empty list is returned.

    """
    store_item = utility.extract_store_file('dropdown')
    if store_item is not None:
        shape_file = config.json_store_location + store_item
        with open(shape_file) as json_file:
            data = json.load(json_file)
            if dropdown_name in data.keys():
                return data[dropdown_name]
    return []


def is_related(json_object, child) -> bool:
    """Identifies if the attribute is a child in the relationship

    if the child is part of a defined relationship it will be created when the dropdown values of the parent are
    processed, otherwise it needs to be ignored.

    :parameter shape_dict the product shape dictionary
    :parameter child the attribute to search for
    :return bool False if the child is not related otherwise it will return True
    """
    if JsonKeys.related.value not in json_object.keys():
        return False
    related = json_object[JsonKeys.related.value]
    for relationship in related:
        if relationship['CHILD'] == child:
            return True
    return False
