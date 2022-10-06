""" The main processing module

The import file defined in the configuration is read in and processed.
Once tokenized the information is handed off to the generation of the
mind map.
"""
import sys
import spacy
from spacy.matcher import Matcher
from spacy.matcher import PhraseMatcher
from spacypdfreader import pdf_reader
from spacy.lang.en.stop_words import STOP_WORDS
import config
import rules
from constants import COVERAGE_WORDS, COMMON_CONVERSIONS
from utility import wise_monkey_says, to_title, load_phrase_files, write_tokens
from xmind_generate import generate_xmind

spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS


def remove_cover_words():
    """Remove the coverage term from the identified coverage name

    Depending on the naming convention used in the policy wording coverages may be described as
    XXX Coverage, the word coverage adds clutter to the generated mind map. If the option
    remove_coverage_from_label is set to Yes or True the coverage clutter will be removed.

    :return bool
    """
    remove_words = False
    check_words = config.config_dict['Process']['remove_coverage_from_label'].lower()
    if check_words == 'yes' or check_words == 'true':
        remove_words = True
    return remove_words


def read_document(nlp):
    """Processes the PDF identified in the configuration

    Reads the PDF identified in the configuration file Base Information -> input_document
    The process will pass the information through the processing twice, while the first pass
    could be written to specific convert pdf to text, this process would not save much
    time as the conversion to text take the majority of the processing. Other conversions
    have been tested and none are as accurate.

    :param nlp The loaded nlp object
    :return spaCy Doc
    """
    input_document = config.config_dict['Base Information']['input_document']
    wise_monkey_says(f'Reading Document from {input_document}')
    wise_monkey_says(f'Please be patient, this will take but a moment')
    wise_monkey_says('... Performing first pass to convert PDF to text')

    doc = pdf_reader(input_document, nlp)

    wise_monkey_says('... Removing stopwords from the document')

    final_text_list = []
    final_text = ' '
    for token in doc.text.split():
        if token.lower() not in spacy_stopwords:
            final_text_list.append(token)
    final_text = final_text.join(final_text_list)

    wise_monkey_says('... Performing second pass to tokenize the text')

    doc = nlp(final_text)

    return doc


def apply_phrase_rules(nlp):
    """Adds the phrases to be searched for and processes the document

    Phrases are added as a first search in the document,
    """
    wise_monkey_says('Building and applying Phrase Rules')
    new_matcher = PhraseMatcher(nlp.vocab)

    load_phrase_files()
    patterns = [nlp(phrase) for phrase in config.matcher_phrases]
    new_matcher.add("COVERAGE_PATTERN", patterns)

    doc = read_document(nlp)

    coverages = dict()
    matches = new_matcher(doc)
    for match_id, start, end in matches:
        matched_text = doc[start:end]
        final_text = ''
        for t in matched_text:
            if t.is_punct or t.pos_ == 'PART':
                ...
            else:
                if not (remove_cover_words() and t.text.lower() in COVERAGE_WORDS):
                    final_text = final_text + ' ' + t.text_with_ws

        final_text = final_text.replace('  ', ' ')
        proper_name = to_title(final_text.strip())
        if proper_name in COMMON_CONVERSIONS.keys():
            added_name = COMMON_CONVERSIONS[proper_name]
        else:
            added_name = proper_name
        coverages[added_name] = {'NAME': added_name, 'CATEGORY': 'Primary Coverages'}
    return coverages, doc


def apply_rules(nlp, doc):
    wise_monkey_says('Building and applying Matcher Rules')
    new_matcher = Matcher(nlp.vocab)
    rules.build_matcher_rules(new_matcher)

    coverages = dict()
    matches = new_matcher(doc)
    for match_id, start, end in matches:
        matched_text = doc[start:end]
        final_text = ''
        for t in matched_text:
            if t.is_punct or t.pos_ == 'PART':
                ...
            else:
                if not (remove_cover_words() and t.text.lower() in COVERAGE_WORDS):
                    final_text = final_text + ' ' + t.text_with_ws

        final_text = final_text.replace('  ', ' ')
        proper_name = to_title(final_text.strip())
        if proper_name in COMMON_CONVERSIONS.keys():
            added_name = COMMON_CONVERSIONS[proper_name]
        else:
            added_name = proper_name
        coverages[added_name] = {'NAME': added_name, 'CATEGORY': 'Primary Coverages'}
    return coverages


def process():
    """ Main processing function

    Processes the PDF file if it is available, this will first perform phrase matching
    then apply rules matching to derive a set of coverages. When there is not input file
    given the mind map will correspond to the product shape defined in the configuration
    file.

    If a regular mind map is to be generated the regular product defined in the
    configuration file will be used to construct the mind map.
    """
    if not ('input_document' in config.config_dict['Base Information']) and not config.is_regular_product:
        wise_monkey_says(f'No Input file given, generating only the shape for {config.product_shape}')
        coverages = dict()
    elif config.is_regular_product:
        if 'regular_product' in config.config_dict['Product Information'].keys():
            config.regular_product = config.config_dict['Product Information']['regular_product']
            config.regular_product_lower = config.regular_product.lower()
            wise_monkey_says(f'Looks like you are creating a Regular product based on {config.regular_product}')
            coverages = dict()
        else:
            wise_monkey_says(
                f'If you want to build a regular product please set "regular_product" in the configuration file')
            wise_monkey_says(f'We will try again after you correct the configuration file')
            sys.exit(1)
    else:
        nlp = spacy.load("en_core_web_md")
        spacy_punctuation = spacy.lang.en.punctuation
        phrase_coverages, doc = apply_phrase_rules(nlp)
        write_tokens(doc)
        rule_coverages = apply_rules(nlp, doc)
        merged_coverages = dict()

        for key in phrase_coverages.keys():
            merged_coverages[key] = phrase_coverages[key]
        for key in rule_coverages.keys():
            merged_coverages[key] = rule_coverages[key]

        coverages = []
        for key in merged_coverages:
            coverages.append(merged_coverages[key])
    wise_monkey_says(f'Generating the {config.product_shape} Mind Map')

    generate_xmind(coverages)

    wise_monkey_says('All done and you are welcome, it is always a pleasure to help')
    wise_monkey_says(f'You will find the mind map at {config.output_file_location}')
    wise_monkey_says('Please deposit one banana for services rendered')
