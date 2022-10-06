version_number = '0.4'

JSON_KEYS = dict()
JSON_KEYS['attributes'] = 'ATTRIBUTES'
JSON_KEYS['related'] = 'RELATED'
JSON_KEYS['attribute_category'] = 'ATTRIBUTE_CATEGORY'
JSON_KEYS['coverage_category'] = 'COVERAGE_CATEGORY'
JSON_KEYS['coverages'] = 'COVERAGES'
JSON_KEYS['risk_objects'] = 'RISK_OBJECTS'
JSON_KEYS['category'] = 'CATEGORY'
JSON_KEYS['line'] = "LINE"

#
# When coverage words are to be removed it will check against this list and not add the name to the label of the
# topic
#
COVERAGE_WORDS = ['cover', 'coverage']

#
# MARKERS are the icons added to the topics
#
MARKERS = dict()
MARKERS['attribute_category'] = 'gw_question'
MARKERS['boolean'] = 'gw_boolean'
MARKERS['clause_category'] = 'gw_clause_category'
MARKERS['coverage'] = 'gw_coverage'
MARKERS['date_time'] = 'gw_date_time'
MARKERS['dropdown'] = 'gw_drop_down'
MARKERS['exposure'] = 'gw_exposure'
MARKERS['info'] = 'symbol-info'
MARKERS['line'] = 'gw_line'
MARKERS['location'] = 'gw_location'
MARKERS['money'] = 'gw_money'
MARKERS['number'] = 'gw_integer'
MARKERS['product'] = 'gw_product'
MARKERS['risk_object'] = 'gw_risk_object'
MARKERS['text'] = 'gw_text'

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
