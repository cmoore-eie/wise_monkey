import json
import xmind
import config
from constants import JsonKeys, Markers

simpleAttributeLabels = [
    Markers.text.value, Markers.number.value, Markers.boolean.value,
    Markers.date_time.value, Markers.money.value
]


# main() method to run standalone
# call readXmind(path) method to call from python
def process_from_xmind():
    read_xmind_output_json()


# Method that does all the work and your entry point
# into reading the xmind
def read_xmind_output_json():
    # Load mindmap
    workbook = xmind.load(config.input_xmind_document)

    # Assume only one sheet
    sheet = workbook.getPrimarySheet()

    # Root Topic is the product
    # Not interested in the 'product' for JSON
    product = sheet.getRootTopic()

    # First sub topic of the product is
    # the line (assuming there is one and only one line)
    line = product.getSubTopics()[0]

    # collect risk_objects
    risk_objects = []
    for xmind_risk_object in line.getSubTopics():
        # Markers define an object as a risk object
        for marker in xmind_risk_object.getMarkers():
            if marker.getMarkerId() and str(marker.getMarkerId()) == Markers.risk_object.value:
                risk_objects.append(create_risk_object_from_xmind_ro(xmind_risk_object))

    output_json(risk_objects)


# xmind_risk_object is a xmind Topic
# This method will build the Risk Object
# and also all child elements of the risk object
def create_risk_object_from_xmind_ro(xmind_risk_object):
    # Basic Attributes
    risk_object = dict()
    risk_object[JsonKeys.name.value] = xmind_risk_object.getTitle()
    risk_object[JsonKeys.type.value] = Markers.risk_object.name

    if xmind_risk_object.getLabels():
        risk_object[JsonKeys.label.value] = ''.join(xmind_risk_object.getLabels())

    risk_object[JsonKeys.attribute_category.value] = []
    risk_object[JsonKeys.attributes.value] = []
    risk_object[JsonKeys.coverage_category.value] = []
    risk_object[JsonKeys.coverages.value] = []

    # Now for the children
    if xmind_risk_object.getSubTopics():
        process_attributes(xmind_risk_object, risk_object)
        process_coverage_categories(xmind_risk_object, risk_object)

    return risk_object


def process_attributes(parent_topic, risk_object):
    """Process attributes associated to a topic

    The tree is traversed to identify all the attributes, it is assumed
    all sub-topics will be attributes if they don't have a clause_category
    as the parent
    """

    for sub_topic in parent_topic.getSubTopics():
        attribute_json = dict()
        if marker_exists(sub_topic.getMarkers(), Markers.clause_category):
            return

        marker = find_marker(sub_topic.getMarkers())

        if marker is not None:

            attribute_json = create_attribute(sub_topic, marker)
            if marker == Markers.attribute_category:
                risk_object[JsonKeys.attribute_category.value].append(attribute_json)
            else:
                risk_object[JsonKeys.attributes.value].append(attribute_json)

        if has_subtopics(sub_topic):
            process_attributes(sub_topic, attribute_json)


def check_valid_marker(xmind_topic) -> bool:
    """Checks for a valid marker

    Valid markers are the Markers defined as needed to process the Json in the
    json to xmind process. So long as one marker corresponds then it will be True
    """
    for marker_to_test in xmind_topic.getMarkers():
        if str(marker_to_test.getMarkerId()) in [marker.value for marker in Markers]:
            return True
    return False


def process_coverage_categories(xmind_parent_topic, risk_object):
    coverage_categories = []
    coverages = []

    for sub_topic in xmind_parent_topic.getSubTopics():
        if marker_exists(sub_topic.getMarkers(), Markers.clause_category):
            coverage_category = dict()
            coverage_category[JsonKeys.name.value] = sub_topic.getTitle()
            coverage_category[JsonKeys.type.value] = Markers.clause_category.name
            if sub_topic.getLabels():
                coverage_category[JsonKeys.label.value] = ''.join(sub_topic.getLabels())
            coverage_categories.append(coverage_category)

            if len(sub_topic.getSubTopics()) > 0:
                process_coverages(sub_topic, coverages)

    risk_object[JsonKeys.coverage_category.value].append(coverage_categories)
    risk_object[JsonKeys.coverages.value].append(coverages)


def process_coverages(parent_topic, coverages: list):
    for sub_topic in parent_topic.getSubTopics():
        if marker_exists(sub_topic.getMarkers(), Markers.coverage):
            coverage = dict()
            coverage[JsonKeys.name.value] = sub_topic.getTitle()
            coverage[JsonKeys.category.value] = parent_topic.getTitle()
            coverage[JsonKeys.type.value] = Markers.coverage.name
            coverages.append(coverage)


def create_exposure_from_xmind_exposure(xmind_exposure):
    exposure = dict()
    # Basic Attributes
    exposure[JsonKeys.name.value] = xmind_exposure.getTitle()
    exposure[JsonKeys.type.value] = 'exposure'
    if xmind_exposure.getLabels():
        exposure[JsonKeys.label.value] = ''.join(xmind_exposure.getLabels())

    exposure[JsonKeys.attributes.value] = []
    # Now for the children
    for xmind_exposure_child in xmind_exposure.getSubTopics():
        for marker in xmind_exposure_child.getMarkers():
            marker_id_str = str(marker.getMarkerId())
            # We either have simple attributes
            if marker_id_str in simpleAttributeLabels:
                exposure[JsonKeys.attributes.value].append(
                    create_attribute(
                        xmind_exposure_child,
                        get_json_type_from_xmind_marker_id_str(marker_id_str)))

                # Create Dropdown attribute
            elif marker_id_str == Markers.dropdown.value:
                exposure[JsonKeys.attributes.value].append(create_dropdown_attribute(xmind_exposure_child))

            # or we have further exposures
            # then recursion
            elif marker_id_str == Markers.exposure.value:
                exposure[JsonKeys.attributes.value].append(create_exposure_from_xmind_exposure(xmind_exposure_child))

    return exposure


def create_dropdown_attribute(xmind_dropdown, category=None):
    attribute_dropdown = dict()
    attribute_dropdown[JsonKeys.name.value] = xmind_dropdown.getTitle()
    attribute_dropdown[JsonKeys.type.value] = Markers.dropdown.name
    if xmind_dropdown.getLabels():
        attribute_dropdown[JsonKeys.label.value] = ''.join(xmind_dropdown.getLabels())
    if category is not None:
        attribute_dropdown[JsonKeys.attribute_category.value] = category
    attribute_dropdown[JsonKeys.options.value] = []
    # Now create the options
    for xmind_option in xmind_dropdown.getSubTopics():
        if check_valid_marker(xmind_option):
            dd_option = dict()
            dd_option[JsonKeys.name.value] = xmind_option.getTitle().strip()
            dd_option[JsonKeys.type.value] = get_json_type_from_xmind_type(xmind_option)
            if xmind_option.getLabels():
                dd_option[JsonKeys.label.value] = ''.join(xmind_option.getLabels())
            attribute_dropdown[JsonKeys.options.value].append(dd_option)

    return attribute_dropdown


def create_attribute(xmind_topic, attribute_type: Markers, category=None):
    attribute = dict()
    attribute[JsonKeys.name.value] = xmind_topic.getTitle().strip()
    if xmind_topic.getLabels():
        attribute[JsonKeys.label.value] = ''.join(xmind_topic.getLabels())
    if category is not None:
        attribute[JsonKeys.attribute_category.value] = category

    attribute[JsonKeys.type.value] = attribute_type.name
    if attribute_type == Markers.dropdown:
        attribute[JsonKeys.options.value] = []
    return attribute


# Call method to print to CLI and file
def output_json(risk_objects):
    output_file_path = config.input_xmind_document.replace('.xmind', '.json')
    json_map = {
        JsonKeys.line.value: {
            JsonKeys.attributes.value: [],
            JsonKeys.attribute_category.value: [],
            JsonKeys.coverage_category.value: []
        },
        JsonKeys.risk_objects.value: risk_objects
    }
    print(json.dumps(json_map))
    with open(output_file_path, "w") as json_file:
        json.dump(json_map, json_file)


# UTIL METHODS
# find marker in topic first, then return MARKERS key
def get_json_type_from_xmind_type(xmind_topic) -> str:
    json_type = ""
    for marker in xmind_topic.getMarkers():
        json_type = get_json_type_from_xmind_marker_id_str(str(marker.getMarkerId()))
    return json_type


# if you have the string representation of the marker id
# find the key in the MARKERS map
def get_json_type_from_xmind_marker_id_str(xmind_marker_id_str):
    return Markers(xmind_marker_id_str).name


def marker_exists(markers, marker: Markers):
    """Test for the existence of a given marker"""
    for test_marker in markers:
        if str(test_marker.getMarkerId()) == marker.value:
            return True
    return False


def find_marker(token_markers) -> Markers:
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


def has_subtopics(token) -> bool:
    if len(token.getSubTopics()) > 0:
        return True
    else:
        return False
