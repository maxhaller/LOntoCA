from rdflib import Namespace


# Classes of interest
# kopf1-ve:         Collective Agreements
# kvgkopf:          Sections
# para:             Paragraph
# absatz:           Section (of a Paragraph)
# intended_list:    Enumeration
NODE_TYPES = ['kopf1-ve', 'kvgkopf', 'para', 'absatz', 'intended_list']

# These node types do not contain children
NON_NESTED_NODE_TYPES = ['kopf1-ve', 'kvgkopf']

# Each class has its own heading class (e.g. kopf1) and tag name (e.g. div)
HEADING_CLASS_NAMES = {
    NODE_TYPES[0]: ['div', 'kopf1'],
    NODE_TYPES[1]: ['div', 'dokheadline_bigger'],
    NODE_TYPES[2]: ['div', 'dokheadline'],
    NODE_TYPES[3]: ['span', 'absnr'],
    NODE_TYPES[4]: ['div', 'list_nr']
}

# Each node type has its own tag
TAGS_PER_CLASS = {
    NODE_TYPES[0]: 'div',
    NODE_TYPES[1]: 'div',
    NODE_TYPES[2]: 'div',
    NODE_TYPES[3]: 'div',
    NODE_TYPES[4]: 'div'
}

# Class of the highest 'level' meaning its parent is always the root node
SUB_ROOT_CLASS = 'kopf1-ve'

# Class of paragraph (entry-point for nested nodes)
PARA_CLASS = 'para'

# Namespace
BASE_NS = 'https://semantics.id/ns/'
CA_NS = Namespace(BASE_NS + 'CollectiveAgreement#')
RE_NS = Namespace(BASE_NS + 'resource/')

# Dict for Months
month_dict = {
    'jänner': 1,
    'jannuar': 1,
    'februar': 2,
    'märz': 3,
    'april': 4,
    'mai': 5,
    'juni': 6,
    'juli': 7,
    'august': 8,
    'september': 9,
    'oktober': 10,
    'november': 11,
    'dezember': 12
}

# List of files that cannot be parsed
TO_BE_DELETED = [
    './data/html/detail-aehrenstolz-backwaren-u-muehlenind-arb.html',
    './data/html/detail-auslaendische-luftverkehrsgesellschaften-in-oest-htv-ang.html',
    './data/html/detail-baeuerliche-betriebe-stm-arb.html',
    './data/html/detail-baeuerliche-betriebe-s-arb.html',
    './data/html/detail-bordpersonal-austrian-air-services-ang.html',
    './data/html/detail-bordpersonal-austrian-airlines-und-lauda-air-ang.html',
    './data/html/detail-do-b-kfa-aerzte-und-dentisten-ang.html', # IMPOSSIBLE TO PARSE! Wrong classes!!
    './data/html/detail-donauschiffahrt-arb.html',
    './data/html/detail-general-kv-urlaubsgesetz-entgelt-arb-ang.html',
    './data/html/detail-int-schlafwagen-und-touristikges-werkstaette-wien-arb.html',
    './data/html/detail-landeskuranstalten-ooe-arb-ang.html',
    './data/html/detail-landwirtschaftliche-gutsbetriebe-stm-arb.html',
    './data/html/detail-landwirtschaftliche-gutsbetriebe-s-arb.html',
    './data/html/detail-landwirtschaftsbetriebe-gemeinde-wien-arb.html',
    './data/html/detail-lauda-air-bordpersonal-ang.html',
    './data/html/detail-konsum-arb.html',
    './data/html/detail-mieder-und-waeschewarenerzeuger-arb.html',
    './data/html/detail-steiermaerkische-landesbahnen-ang.html',
    './data/html/detail-suesswarenindustrie-konsolidiert-ang.html',
    './data/html/detail-taxi-vlb-arb.html',
    './data/html/detail-zementindustrie-arb.html'
]