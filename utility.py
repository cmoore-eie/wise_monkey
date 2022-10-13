import json
import os.path
import re
import sys
from json import JSONDecodeError

import config
from product_shapes import dropdown_to_dict, is_related
from constants import Markers, JsonKeys
import pandas as pd


def add_xmind_attributes(topic, json_object):
    """ Add attributes to the mind map

    Using the Json file that contains the information about the product shape the first set of
    attributes that are not attached to a category are processed first, this ensures they appear
    as the first set of attribute.

    The second part of the process adds the categories and processes the attributes
    that are attached to the category.

    :parameter topic The topic used for attachment
    :parameter json_object json containing the object structure
    """

    attributes = json_object[JsonKeys.attributes.value]
    attribute_no_category(attributes, topic, json_object)
    attribute_with_category(attributes, topic, json_object)


def attribute_no_category(attributes, topic, json_object):
    """Add attributes that don't have a corresponding category"""
    for attribute in attributes:
        if not (is_related(json_object, attribute['NAME'])):
            if JsonKeys.category.value not in attribute:
                added_attribute = add_attribute(attribute, topic, json_object)
                process_additional_attributes(attribute, added_attribute, json_object)


def attribute_with_category(attributes, topic, json_object):
    """Add the attributes that have a corresponding category

    The first part of the process is to add the attribute
    categories then add the attributes to the corresponding
    category
    """
    if JsonKeys.attribute_category.value in json_object.keys():
        question_category_topic = add_question_categories(topic, json_object)
        for attribute in attributes:
            if JsonKeys.category.value in attribute.keys():
                if not (is_related(json_object, attribute['NAME'])):
                    added_attribute = add_attribute(attribute, topic, json_object, question_category_topic)
                    process_additional_attributes(attribute, added_attribute, json_object)


def add_question_categories(topic, json_object) -> dict:
    """ Adds the question (Attribute) categories to the mind map

    Question Categories are added to the topic that is passed in,
    as there could be multiple added at the same time the new
    topics (Question Categories) are added to a dictionary that
    is used to add the correct attributes to the correct question
    categories

    :parameter topic The topic that will be used to add the question categories to
    :parameter category_key The key to the category section, 'Attribute Category', 'Line Attribute Category'
    """
    question_category_topic = dict()
    if JsonKeys.attribute_category.value in json_object.keys():
        question_categories = json_object[JsonKeys.attribute_category.value]
        for question_category in question_categories:
            item = topic.addSubTopic()
            item.setTitle(question_category['NAME'])
            item.addMarker(Markers[question_category['TYPE']].value)
            if 'LABEL' in question_category.keys():
                item.addLabel(question_category['LABEL'])
            question_category_topic[question_category['NAME']] = item
    return question_category_topic


def add_coverage_categories(topic, json_object) -> dict:
    coverage_category_topic = dict()
    if JsonKeys.coverage_category.value in json_object.keys():
        coverage_categories = json_object[JsonKeys.coverage_category.value]
        for coverage_category in coverage_categories:
            item = topic.addSubTopic()
            item.setTitle(coverage_category['NAME'])
            item.addMarker(Markers[coverage_category['TYPE']].value)
            if 'LABEL' in coverage_category.keys():
                item.addLabel(coverage_category['LABEL'])
            coverage_category_topic[coverage_category['NAME']] = item
    return coverage_category_topic


def add_dropdown(attribute, item, json_object):
    if 'LIST' in attribute.keys():
        dropdown_name = attribute['LIST']
    else:
        dropdown_name = attribute['NAME']
    if 'OPTIONS' in attribute.keys():
        dropdown_data = attribute['OPTIONS']
    else:
        dropdown_data = dropdown_to_dict(dropdown_name)

    if len(dropdown_data) == 0:
        return

    process_dropdown_items(dropdown_data, item, attribute, json_object)


def process_dropdown_items(dropdown_data, item, attribute, json_object):
    for dropdown_value in dropdown_data:
        if type(dropdown_value) == dict:
            item_option = item.addSubTopic()
            item_option.setTitle(dropdown_value['NAME'])
            if 'TYPE' in dropdown_value.keys():
                item_option.addMarker(Markers[dropdown_value['TYPE']].value)
            else:
                item_option.addMarker(Markers.text.value)
            if 'LABEL' in dropdown_value.keys():
                item_option.addLabel(dropdown_value['LABEL'])
            extract_related(json_object, attribute['NAME'], dropdown_value['NAME'], item_option)
            process_additional_attributes(dropdown_value, item_option, json_object)

        else:
            item_option = item.addSubTopic()
            item_option.setTitle(dropdown_value)
            item_option.addMarker(Markers.text.value)
            extract_related(json_object, attribute['NAME'], dropdown_value, item_option)


def process_additional_attributes(existing_value, topic, json_object):
    if JsonKeys.attributes.value in existing_value:
        for additional_attribute in existing_value[JsonKeys.attributes.value]:
            add_attribute(additional_attribute, topic, json_object)


def add_attribute(attribute, topic, json_object, question_category_topic=None):
    copy_topic = topic
    if JsonKeys.category.value in attribute.keys():
        if question_category_topic is not None:
            if JsonKeys.category.value in attribute.keys():
                copy_topic = question_category_topic[attribute[JsonKeys.category.value]]

    item = copy_topic.addSubTopic()
    item.setTitle(attribute[JsonKeys.name.value])
    item.addMarker(Markers[attribute[JsonKeys.type.value]].value)
    if JsonKeys.label.value in attribute.keys():
        item.addLabel(attribute[JsonKeys.label.value])
    if JsonKeys.attributes.value in attribute.keys():
        for attribute_attribute in attribute[JsonKeys.attributes.value]:
            add_attribute(attribute_attribute, item, json_object)

    if attribute[JsonKeys.type.value] == 'dropdown':
        add_dropdown(attribute, item, json_object)
    return item


def add_xmind_coverages(coverages, json_object, topic):
    """Create the coverages in the mind map

    Coverages should belong to a category, and they are created first, once
    created the coverages are added to the correct category. If there are any terms
    these are added to the coverage by using the add attribute function, terms could
    include risk objects when a coverage schedule is created, these have attributes
    and this is passed to the standard add attribute process.

    :parameter coverages (list) A list of coverage dicts
    :parameter topic (topic) The base topic to attach the coverages to
    :parameter category_key The dictionary key for the coverage categories
    """
    if JsonKeys.coverage_category.value in json_object.keys():
        coverage_categories = add_coverage_categories(topic, json_object)
        for coverage in coverages:
            if JsonKeys.category.value in coverage:
                topic_to_use = coverage_categories[coverage['CATEGORY']]
            else:
                topic_to_use = topic
            build_coverage(topic_to_use, coverage, json_object)
    else:
        wise_monkey_says_oops(f'Coverages must have a category and none are defined for {json_object["NAME"]}')


def build_coverage(topic_to_use, coverage, json_object):
    new_coverage = topic_to_use.addSubTopic()
    new_coverage.setTitle(coverage[JsonKeys.name.value])
    new_coverage.addMarker(Markers.coverage.value)
    if JsonKeys.label.value in coverage.keys():
        new_coverage.addLabel(coverage[JsonKeys.label.value])

    if JsonKeys.terms.value in coverage.keys():
        for term in coverage[JsonKeys.terms.value]:
            add_attribute(term, new_coverage, json_object)


def extract_related(json_object, parent, link, topic):
    if JsonKeys.related.value not in json_object.keys():
        return
    related = json_object[JsonKeys.related.value]
    attributes = json_object[JsonKeys.attributes.value]
    for relationship in related:
        if relationship[JsonKeys.parent.value] == parent and relationship[JsonKeys.link.value] == link:
            for attribute in attributes:
                if attribute[JsonKeys.name.value] == relationship['CHILD']:
                    add_attribute(attribute, topic, json_object)


def wise_monkey_says(message):
    to_say = f'Wise Monkey has spoken - {message}'
    print(to_say)


def wise_monkey_says_oops(message):
    to_say = f'Wise Monkey OOPS - {message}'
    print(to_say)


def to_title(string) -> str:
    regex = re.compile("[a-z]+('[a-z]+)?", re.I)
    return regex.sub(lambda grp: grp.group(0)[0].upper() + grp.group(0)[1:].lower(),
                     string)


def load_shape_files():
    json_store_file = config.json_store_location + 'json_store.json'
    try:
        with open(json_store_file) as json_file:
            list_items = json.load(json_file)['Json Store']
            for item in list_items:
                config.json_store_files.append(item)
    except JSONDecodeError:
        wise_monkey_says_oops(f"The json file json_store.json can't be processed")
        sys.exit(1)


def load_phrase_files():
    file_key = f'{config.product_shape_lower} phrases'
    store_item = extract_store_file(file_key)

    if store_item is None:
        return

    file_path = f'{config.json_store_location}{store_item}'
    if os.path.exists(file_path):
        try:
            with open(file_path) as json_file:
                list_items = json.load(json_file)['Phrases']
                for item in list_items:
                    config.matcher_phrases.append(item['NAME'])
        except JSONDecodeError:
            ...


def write_tokens(doc):
    token_text = []
    token_lemma = []
    token_pos = []
    token_tag = []
    token_dep = []
    token_shape = []
    token_is_alpha = []
    token_is_title = []

    output_tokens = config.config_dict['Process']['output_tokens'].lower()
    if output_tokens == 'yes' or output_tokens == 'true':
        excel_file = config.config_dict['Base Information']['output_document']
        excel_file = excel_file.replace('xmind', 'xlsx')
        wise_monkey_says(f'... I will now write the token information to {excel_file}')
        for token in doc:
            token_text.append(token.text)
            token_lemma.append(token.lemma_)
            token_pos.append(token.pos_)
            token_tag.append(token.tag_)
            token_dep.append(token.dep_)
            token_shape.append(token.shape_)
            token_is_alpha.append(token.is_alpha)
            token_is_title.append(token.is_title)

        token_set = pd.DataFrame({
            'text': token_text,
            'lemma': token_lemma,
            'pos': token_pos,
            'tag': token_tag,
            'dep': token_dep,
            'shape': token_shape,
            'is_alpha': token_is_alpha,
            'is_title': token_is_title
        })

        token_set.to_excel(excel_file, sheet_name='tokens')


def extract_store_file(search_item):
    """Extract the store name from the store list"""
    for item in config.json_store_files:
        product = item["PRODUCT"]
        shape = item['SHAPE']
        language = item['LANGUAGE']
        if product == search_item and language == config.language:
            return shape
    return None
