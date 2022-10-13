import shutil
from datetime import date
import xmind

import config
import product_shapes
from constants import Markers, JsonKeys, GeneralConstants
from product_shapes import extract_shape
from utility import add_xmind_attributes, add_xmind_coverages

standard_term_types = {
    'Sum Insured': Markers.money.value,
    'Limit': Markers.money.value,
    'Deductible': Markers.money.value
}


def standard_terms(coverage):
    terms_indicator = config.config_dict['Mind Map']['add_basic_terms'].lower()
    if terms_indicator != 'yes' and terms_indicator != 'true':
        return

    for key in standard_term_types:
        term = coverage.addSubTopic()
        term.setTitle(key)
        term.addMarker(standard_term_types[key])


def apply_product_shape(line, coverages):
    product_shapes.apply_shape(line, coverages)


def apply_standard_product_shape(line, coverages):
    risk_object = line.addSubTopic()
    risk_object.setTitle("Risk Object")
    risk_object.addMarker(Markers.risk_object.value)

    risk_object_notes = risk_object.addSubTopic()
    risk_object_notes.setTitle("Notes")
    risk_object_notes.addMarker(Markers.info.value)

    risk_object_attribute = risk_object.addSubTopic()
    risk_object_attribute.setTitle("Attributes")

    risk_object_coverage = risk_object.addSubTopic()
    risk_object_coverage.setTitle("Coverages")
    risk_object_coverage_category = risk_object_coverage.addSubTopic()
    risk_object_coverage_category.setTitle("Primary Coverages")
    risk_object_coverage_category.addMarker(Markers.clause_category.value)

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

    for coverage in coverages:
        new_coverage = risk_object_coverage_category.addSubTopic()
        new_coverage.setTitle(coverages[coverage])
        new_coverage.addMarker(Markers.coverage.value)
        standard_terms(new_coverage)


def apply_about(line):
    line_about = line.addSubTopic()
    line_about.setTitle("About")
    line_about.addMarker(Markers.info.value)
    line_about_version = line_about.addSubTopic()
    line_about_version.setTitle('Version')
    info = line_about_version.addSubTopic()
    info.setTitle('1.0')

    line_about_date = line_about.addSubTopic()
    line_about_date.setTitle('Date')
    info = line_about_date.addSubTopic()
    info.setTitle(date.today().isoformat())

    line_about_author = line_about.addSubTopic()
    line_about_author.setTitle('Author')
    info = line_about_author.addSubTopic()
    info.setTitle('Wise Monkey')

    line_about_description = line_about.addSubTopic()
    line_about_description.setTitle('Description')
    if config.is_regular_product:
        description = f'Built from Regular Product = {config.regular_product}'
    else:
        description = f'Auto Generated {config.product_shape} product'
    info = line_about_description.addSubTopic()
    info.setTitle(description)


def build_sheet(sheet1, coverages):
    if config.is_regular_product:
        extract_shape(config.regular_product_lower)
    else:
        extract_shape(config.product_shape_lower)

    sheet1.setTitle("Product")

    product = sheet1.getRootTopic()
    product_label = config.config_dict[GeneralConstants.product_information.value]['product_label'].replace(' ', '')
    product.setTitle(config.config_dict[GeneralConstants.product_information.value]['product_name'])
    product.addLabel(product_label)
    product.addMarker(Markers.product.value)

    line = product.addSubTopic()
    line_label = config.config_dict[GeneralConstants.product_information.value]['line_label'].replace(' ', '')
    line.setTitle(config.config_dict[GeneralConstants.product_information.value]['line_name'])
    line.addLabel(line_label)
    line.addMarker(Markers.line.value)

    apply_about(line)

    line_notes = line.addSubTopic()
    line_notes.setTitle("Notes")
    line_notes.addMarker(Markers.info.value)

    line_attribute = line.addSubTopic()
    line_attribute.setTitle("Attributes")
    if JsonKeys.line.value in config.shape_dict.keys():
        json_line_object = config.shape_dict[JsonKeys.line.value]
        if JsonKeys.attributes.value in json_line_object.keys():
            add_xmind_attributes(line_attribute, json_line_object)

        line_coverage = line.addSubTopic()
        line_coverage.setTitle("Coverages")

        if len(config.input_document) == 0:
            if JsonKeys.coverages.value in json_line_object.keys():
                coverages = json_line_object[JsonKeys.coverages.value]
                add_xmind_coverages(coverages, json_line_object, line_coverage)

    line_exclusions = line.addSubTopic()
    line_exclusions.setTitle("Exclusions")

    line_conditions = line.addSubTopic()
    line_conditions.setTitle("Conditions")

    apply_product_shape(line, coverages)


def generate_xmind(coverages):
    config.output_file_location = config.config_dict['Base Information']['output_document']
    shutil.copyfile('APDBase.xmind', config.output_file_location)
    workbook = xmind.load(config.output_file_location)
    sheet1 = workbook.getPrimarySheet()
    build_sheet(sheet1, coverages)

    xmind.save(workbook, path=config.output_file_location)
