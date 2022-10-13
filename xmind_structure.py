from constants import Markers


class XmindBase:

    def add_object(self, marker: Markers, attribute=None):
        if self.json_type == Markers.dropdown:
            return self.add_option(marker, attribute)
        if self.json_type == Markers.coverage:
            return self.add_term(marker, attribute)
        if self.json_type == Markers.clause_category:
            return self.add_coverage(attribute)
        return self.add_attribute(marker, attribute)

    def add_attribute(self, marker: Markers, attribute=None):
        if attribute is None:
            attribute = XmindBase()
        attribute.json_type = marker
        self.attributes.append(attribute)
        return attribute

    def add_term(self, marker: Markers, term=None):
        if term is None:
            term = XmindBase()
        term.json_type = marker
        self.terms.append(term)
        return term

    def add_option(self, marker: Markers, attribute=None):
        if attribute is None:
            attribute = XmindBase()
        attribute.json_type = marker
        self.options.append(attribute)
        return attribute

    def add_risk_object(self, risk_object=None):
        if risk_object is None:
            risk_object = XmindBase()
        risk_object.json_type = Markers.risk_object
        self.risk_objects.append(risk_object)
        return risk_object

    def add_coverage(self, coverage_object=None):
        if coverage_object is None:
            coverage_object = XmindBase()
        coverage_object.json_type = Markers.coverage
        self.coverages.append(coverage_object)
        return coverage_object

    def add_clause_category(self, clause_category=None):
        if clause_category is None:
            clause_category = XmindBase()
        clause_category.json_type = Markers.clause_category
        self.coverage_categories.append(clause_category)
        return clause_category

    def add_attribute_category(self, attribute_category=None):
        if attribute_category is None:
            attribute_category = XmindBase()
        attribute_category.json_type = Markers.attribute_category
        self.attribute_categories.append(attribute_category)
        return attribute_category

    def add_line(self, line=None):
        if line is None:
            line = XmindBase()
        line.json_type = Markers.line
        self.lines.append(line)
        return line

    def __init__(self):
        self.name = ''
        self.json_type = None
        self.label = ''
        self.category = ''
        self.options: list[XmindBase] = list()
        self.terms: list[XmindBase] = list()
        self.attributes: list[XmindBase] = list()
        self.attribute_categories: list[XmindBase] = list()
        self.coverages: list[XmindBase] = list()
        self.coverage_categories: list[XmindBase] = list()
        self.lines: list[XmindBase] = list()
        self.risk_objects: list[XmindBase] = list()
