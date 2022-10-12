"""Common Constants

Constant values used in modules to provide a single point
where the values are defined. Where possible Enum is ued
this ensures that there is not change or possibility
of overwriting the values in code
"""
from enum import Enum


class ProcessType(Enum):
    to_xmind = 'json to xmind'
    from_xmind = 'xmind to json'


class GeneralConstants(Enum):
    version_number = '0.4'
    base_information = 'Base Information'
    product_information = 'Product Information'
    language_information = 'Language Information'


class JsonKeys(Enum):
    attributes = 'ATTRIBUTES'
    related = 'RELATED'
    attribute_category = 'ATTRIBUTE_CATEGORY'
    coverage_category = 'COVERAGE_CATEGORY'
    coverages = 'COVERAGES'
    risk_objects = 'RISK_OBJECTS'
    category = 'CATEGORY'
    line = "LINE"
    label = 'LABEL'
    name = 'NAME'
    type = 'TYPE'
    options = 'OPTIONS'


#
# When coverage words are to be removed it will check against this list and not add the name to the label of the
# topic
#
COVERAGE_WORDS = ['cover', 'coverage']


#
# MARKERS are the icons added to the topics
#
class Markers(Enum):
    attribute_category = 'gw_question'
    boolean = 'gw_boolean'
    clause_category = 'gw_clause_category'
    coverage = 'gw_coverage'
    date_time = 'gw_date_time'
    dropdown = 'gw_drop_down'
    exposure = 'gw_exposure'
    info = 'symbol-info'
    line = 'gw_line'
    location = 'gw_location'
    money = 'gw_money'
    number = 'gw_integer'
    product = 'gw_product'
    risk_object = 'gw_risk_object'
    text = 'gw_text'


#
# Common Conversions
#
COMMON_CONVERSIONS = dict()
COMMON_CONVERSIONS['Loss Rent'] = 'Loss of Rent'
COMMON_CONVERSIONS['Selling Home'] = 'Selling Your Home'
COMMON_CONVERSIONS['Increased Cost Working'] = 'Increased Cost of Working'
COMMON_CONVERSIONS['Trace Access'] = 'Trace and Access'
COMMON_CONVERSIONS['Theft Outbuildings'] = 'Theft from Outbuildings'
COMMON_CONVERSIONS['Contents University'] = 'Contents at University'
COMMON_CONVERSIONS['Contents Temporarily Away Home'] = 'Contents Temporarily Away from Home'
COMMON_CONVERSIONS['Theft Unattended Motor Vehicle'] = 'Theft from Unattended Motor Vehicle'
COMMON_CONVERSIONS['Loss Theft Keys'] = 'Loss or Theft of Keys'
COMMON_CONVERSIONS['Water Oil Escaping'] = 'Water or Oil Escaping'
COMMON_CONVERSIONS['Storm Flood'] = 'Storm or Flood'
COMMON_CONVERSIONS['Theft Attempted Theft'] = 'Theft or Attempted Theft'

#
# Default Coverage Categories
#
default_coverage_categories = [
    {"NAME": "Primary Coverages", "TYPE": "clause_category", "LABEL": "PrimaryCC"},
    {"NAME": "Optional Coverages", "TYPE": "clause_category", "LABEL": "OptCC"}
]
