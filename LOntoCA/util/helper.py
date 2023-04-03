from bs4 import BeautifulSoup as Bs, PageElement, NavigableString
from constants import TAGS_PER_CLASS, SUB_ROOT_CLASS, HEADING_CLASS_NAMES, NODE_TYPES


def get_filename(file: str):
    return file.split('\\')[-1].split('.')[0]


def get_anchor_node(collective_agreement: Bs):
    return collective_agreement.find(TAGS_PER_CLASS[SUB_ROOT_CLASS], SUB_ROOT_CLASS)


def handle_title(node: PageElement, node_type: str):
    heading_element = node.find_next(HEADING_CLASS_NAMES[node_type][0], {'class': HEADING_CLASS_NAMES[node_type][1]})
    if heading_element is not None:
        heading_element.extract()
        return node, heading_element.text.strip().replace('\n', ' ')
    else:
        return node, 'NOT FOUND'


def extract_raw_text_from_node(node: PageElement) -> str:
    no_children = True
    node = Bs(str(node), 'html.parser')
    for node_type in NODE_TYPES:
        next = node.find_all(HEADING_CLASS_NAMES[node_type][0], {'class': HEADING_CLASS_NAMES[node_type][1]})
        if next is not None and len(next) > 0:
            no_children = False
            break
    if no_children:
        text = node.text
        return text
    else:
        text = ''.join([t for t in Bs(node.__str__(), 'html.parser').find_all()[0].contents if type(t) == NavigableString])
        return text


def get_node_attribute(node: PageElement, attr: str) -> str | None:
    if node.get(attr) is None:
        return None
    else:
        return node.get(attr)[0]