import json
import xmind
from constants import JsonKeys, Markers
from xmind_structure import XmindBase


def process_from_xmind(input_document_path):
    read_xmind_output_json(input_document_path)


# Method that does all the work and your entry point
# into reading the xmind
def read_xmind_output_json(input_document_path):
    # Load mindmap
    workbook = xmind.load(input_document_path)

    # Assume only one sheet
    sheet = workbook.getPrimarySheet()

    xmind_product = sheet.getRootTopic()
    product = XmindBase()
    process_product(product, xmind_product)
    output_json(product, input_document_path)


def process_product(xmind_base: XmindBase, xmind_token):
    json_object = xmind_base
    for sub_topics in xmind_token.getSubTopics():

        match find_marker(sub_topics.getMarkers()):
            case Markers.line:
                json_object = xmind_base.add_line()
            case Markers.risk_object:
                if xmind_base.json_type is not Markers.line:
                    risk_object = xmind_base.add_object(Markers.risk_object)
                    create_attribute(sub_topics, Markers.risk_object, risk_object)
                    if len(sub_topics.getSubTopics()) > 0:
                        json_object = risk_object
                else:
                    json_object = xmind_base.add_risk_object()
                    json_object.name = sub_topics.getTitle()
            case Markers.coverage:
                json_object = xmind_base.add_coverage()
                json_object.name = sub_topics.getTitle()
            case Markers.clause_category:
                json_object = xmind_base.add_clause_category()
                json_object.name = sub_topics.getTitle()
            case Markers.attribute_category:
                json_object = xmind_base.add_attribute_category()
                json_object.name = sub_topics.getTitle()
            case Markers.text:
                attribute = xmind_base.add_object(Markers.text)
                create_attribute(sub_topics, Markers.text, attribute)
                if len(sub_topics.getSubTopics()) > 0:
                    json_object = attribute
            case Markers.date_time:
                attribute = xmind_base.add_object(Markers.date_time)
                create_attribute(sub_topics, Markers.date_time, attribute)
            case Markers.number:
                attribute = xmind_base.add_object(Markers.number)
                create_attribute(sub_topics, Markers.number, attribute)
            case Markers.money:
                attribute = xmind_base.add_object(Markers.money)
                create_attribute(sub_topics, Markers.money, attribute)
            case Markers.exposure:
                exposure = xmind_base.add_object(Markers.exposure)
                create_attribute(sub_topics, Markers.exposure, exposure)
                if len(sub_topics.getSubTopics()) > 0:
                    json_object = exposure
            case Markers.location:
                attribute = xmind_base.add_object(Markers.location)
                create_attribute(sub_topics, Markers.location, attribute)
            case Markers.boolean:
                attribute = xmind_base.add_object(Markers.boolean)
                create_attribute(sub_topics, Markers.boolean, attribute)
            case Markers.dropdown:
                json_object = xmind_base.add_object(Markers.dropdown)
                create_attribute(sub_topics, Markers.dropdown, json_object)

        if len(sub_topics.getSubTopics()) > 0 and json_object is not None:
            process_product(json_object, sub_topics)


def create_attribute(xmind_topic, attribute_type: Markers, json_object: XmindBase, category=None):
    json_object.name = xmind_topic.getTitle().strip()
    if xmind_topic.getLabels():
        json_object.label = ''.join(xmind_topic.getLabels())
    if category is not None:
        json_object.category = category

    json_object.json_type = attribute_type


# Call method to print to CLI and file
def output_json(product, input_document_path):
    output_file_path = input_document_path.replace('.xmind', '.json')
    json_dict = to_json(product)
    json_string = json.dumps(json_dict)
    with open(output_file_path, "w") as json_file:
        json_file.write(json_string)


def find_marker(token_markers):
    """Identifies the first marker that is defined as a marker for the mind map

    The function will ignore any markers that are not used by APD and will only
    return the first one found as there should only be a single APD marker.
    """
    for token_marker in token_markers:
        marker_str = str(token_marker.getMarkerId())
        for marker in Markers:
            if marker.value == marker_str:
                return marker
    return None


def to_json(xmind_class: XmindBase):
    item_dict = dict()
    xmind_lines = []
    xmind_risk_objects = []
    for line in xmind_class.lines:
        line, risk_objects = line_to_json(line)
        xmind_lines.append(line)
        xmind_risk_objects += risk_objects

    item_dict[JsonKeys.line.value] = xmind_lines
    item_dict[JsonKeys.risk_objects.value] = xmind_risk_objects
    return item_dict


def attribute_category_to_json(attribute_category: XmindBase):
    item_dict = dict()
    item_attributes = []
    item_dict[JsonKeys.name.value] = attribute_category.name
    item_dict[JsonKeys.type.value] = attribute_category.json_type.name
    for attribute in attribute_category.attributes:
        item_attributes.append(attribute_to_json(attribute, attribute_category.name))
    return item_dict, item_attributes


def coverage_category_to_json(coverage_category: XmindBase):
    item_dict = dict()
    item_coverages = []
    item_dict[JsonKeys.name.value] = coverage_category.name
    item_dict[JsonKeys.type.value] = coverage_category.json_type.name
    for coverages in coverage_category.coverages:
        item_coverages.append(coverage_to_json(coverages, coverage_category.name))
    return item_dict, item_coverages


def coverage_to_json(coverage: XmindBase, category=None) -> dict:
    item_dict = dict()
    json_terms = []
    json_attributes = []

    item_dict[JsonKeys.name.value] = coverage.name
    item_dict[JsonKeys.type.value] = coverage.json_type.name

    if len(coverage.label) > 0:
        item_dict[JsonKeys.label.value] = coverage.label
    if category is not None:
        item_dict[JsonKeys.category.value] = category

    for term in coverage.terms:
        json_terms.append(attribute_to_json(term))

    for attribute_item in coverage.attributes:
        json_attributes.append(attribute_to_json(attribute_item))

    if len(json_terms) > 0:
        item_dict[JsonKeys.terms.value] = json_terms
    if len(json_attributes) > 0:
        item_dict[JsonKeys.attributes.value] = json_attributes

    return item_dict


def attribute_to_json(attribute: XmindBase, category=None) -> dict:
    item_dict = dict()
    json_options = []
    json_attributes = []
    item_dict[JsonKeys.name.value] = attribute.name
    item_dict[JsonKeys.type.value] = attribute.json_type.name

    if len(attribute.label) > 0:
        item_dict[JsonKeys.label.value] = attribute.label
    if category is not None:
        item_dict[JsonKeys.category.value] = category

    for option in attribute.options:
        json_options.append(attribute_to_json(option))

    for attribute_item in attribute.attributes:
        json_attributes.append(attribute_to_json(attribute_item))

    if len(json_options) > 0:
        item_dict[JsonKeys.options.value] = json_options
    if len(json_attributes) > 0:
        item_dict[JsonKeys.attributes.value] = json_attributes

    return item_dict


def risk_object_to_json(risk_object: XmindBase) -> dict:
    item_dict = dict()
    json_coverage_categories = []
    json_attribute_categories = []
    json_attributes = []
    json_coverages = []

    item_dict[JsonKeys.name.value] = risk_object.name
    item_dict[JsonKeys.type.value] = risk_object.json_type.name

    if len(risk_object.label) > 0:
        item_dict[JsonKeys.label.value] = risk_object.label

    for attribute in risk_object.attributes:
        json_attributes.append(attribute_to_json(attribute))

    for attribute_category in risk_object.attribute_categories:
        categories, attributes = attribute_category_to_json(attribute_category)
        json_attribute_categories.append(categories)
        json_attributes += attributes

    for coverage_category in risk_object.coverage_categories:
        categories, coverages = coverage_category_to_json(coverage_category)
        json_coverage_categories.append(categories)
        json_coverages += coverages

    item_dict[JsonKeys.attribute_category.value] = json_attribute_categories
    item_dict[JsonKeys.coverage_category.value] = json_coverage_categories
    item_dict[JsonKeys.attributes.value] = json_attributes
    item_dict[JsonKeys.coverages.value] = json_coverages

    return item_dict


def option_to_json():
    ...


def line_to_json(line: XmindBase):
    item_dict = dict()
    json_attribute_categories = []
    json_coverage_categories = []
    json_attributes = []
    json_coverages = []
    json_risk_objects = []

    for attribute_category in line.attribute_categories:
        categories, attributes = attribute_category_to_json(attribute_category)
        json_attribute_categories.append(categories)
        json_attributes += attributes

    for coverage_category in line.coverage_categories:
        categories, coverages = coverage_category_to_json(coverage_category)
        json_coverage_categories.append(categories)
        json_coverages += coverages

    for attribute in line.attributes:
        json_attributes.append(attribute_to_json(attribute))

    for risk_object in line.risk_objects:
        json_risk_objects.append(risk_object_to_json(risk_object))

    item_dict[JsonKeys.attribute_category.value] = json_attribute_categories
    item_dict[JsonKeys.coverage_category.value] = json_coverage_categories
    item_dict[JsonKeys.attributes.value] = json_attributes
    item_dict[JsonKeys.coverages.value] = json_coverages

    return item_dict, json_risk_objects
