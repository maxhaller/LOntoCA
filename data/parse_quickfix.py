from bs4 import BeautifulSoup as Bs, NavigableString, Tag, PageElement
from glob import glob
from tqdm import tqdm


HIERARCHY = ['active', 'kopf1-ve', 'kvgkopf', 'para',
             'abs_gr', 'absatz', 'lit_gr_dist', 'lit_text_liste', 'ueb',
             'intended_list', 'vwgrp', 'vwgrp_dist', 'tabellen_wrapper']

HEADING_LIST = ['kopf1', 'dokheadline_bigger', 'dokheadline', 'abs_grtit', 'absnr', 'abstitel', 'list_nr']

HEADING_DICT = {
    'active': None,
    'kopf1-ve': 'kopf1',
    'kvgkopf': 'dokheadline_bigger',
    'para': 'dokheadline',
    'abs_gr_dist': 'abs_grtit',
    'abs_gr': 'abs_grtit',
    'absatz': ['absnr', 'abstitel'],
    'absatz_litgr': ['absnr', 'abstitel'],
    'intended_list': 'list_nr',
    'vwgrp': 'grptitel',
    'vwgrp_dist': 'grptitel',
    'tabellen_wrapper': '',
    'lit_text_liste': '',
    'ueb': ''
}


def handle_nested_node(element, value_row, index, file_name):
    has_relevant_children = False
    for content in element.contents:
        if isinstance(content, Tag):
            classes = content.get('class')
            if classes is not None:
                for n in HIERARCHY:
                    if n in classes:
                        has_relevant_children = True
                        if not n == 'lit_gr_dist':
                            if isinstance(HEADING_DICT[n], list):
                                bs_element = Bs(content.__str__(), 'html.parser')
                                nr = bs_element.select_one(f'.{HEADING_DICT[n][0]}').text.strip()
                                title_element = bs_element.select_one(f'.{HEADING_DICT[n][1]}')
                                if title_element is None:
                                    title = nr
                                else:
                                    title = nr + title_element.text.replace('\n', '\t').replace('\t\t', '\t').replace('	', ' ').strip()
                            else:
                                if HEADING_DICT[n] != '':
                                    title_element = Bs(content.__str__(), 'html.parser').select_one(f'.{HEADING_DICT[n]}')
                                    if title_element is not None:
                                        title = title_element.text.replace('\n', '\t').replace('\t\t', '\t').replace('	', ' ').strip()
                                    else:
                                        title = 'Not Found'
                                else:
                                    title = n


                            if n == 'lit_text_liste':
                                ul = content.find('ul')
                                if ul is not None:
                                    wrong_label_elements = ul.find_all('li', {'class': 'grey'})
                                    for el in wrong_label_elements:
                                        el['class'] = 'intended_list'
                                    n_contents = len(content.contents)
                                    cs = content.contents
                                    for i in range(n_contents):
                                        if isinstance(cs[i], Tag):
                                            if cs[i].name == 'ul':
                                                cs[i:i+1] = wrong_label_elements
                                else:
                                    n_contents = len(content.contents)
                                    cs = content.contents
                                    for i in range(n_contents):
                                        if isinstance(cs[i], Tag):
                                            if cs[i].name == 'div' and cs[i].get('class') is None:
                                                cs[i] = NavigableString(cs[i].text)

                            if not n == 'tabellen_wrapper':
                                text_content = []
                                for c in content.contents:
                                    if isinstance(c, NavigableString):
                                        text_content.append(c)
                                    if isinstance(c, Tag):
                                        content_classes = c.get('class')
                                        if content_classes is not None:
                                            found = False
                                            for cl in content_classes:
                                                if cl in HIERARCHY or cl in HEADING_LIST:
                                                    found = True
                                            if not found:
                                                if len(c.text.strip()) > 0:
                                                    text_content.append(c.text.strip())
                                        else:
                                            if len(c.text.strip()) > 0:
                                                text_content.append(c.text.strip())

                                if len(text_content) > 0:
                                    elem_text = ''.join(text_content).strip()
                                    if len(elem_text) > 0:
                                        text = title + '###SEP###' + elem_text
                                    else:
                                        text = title
                                else:
                                    text = title

                            else:
                                # Escape double quotes for csv
                                text = title + '###SEP###' + str(content)

                            text = text.replace('"', '""')

                            value_row[index] = text
                            handle_nested_node(content, value_row.copy(), index+1, file_name)
                        else:
                            handle_nested_node(content, value_row.copy(), index, file_name)

    if not has_relevant_children:
        with open(f'./data/csv/{file_name}.csv', 'a', encoding='utf-8') as f:
            f.write(','.join([f'"{s}"' for s in value_row]) + '\n')


def parse_files():
    for file in tqdm(glob('./data/html/detail-*')):
        with open(file, 'r', encoding='utf-8') as f:
            ca = Bs(f.read(), 'html.parser')
            file_name = file.split('\\')[-1].split('.')[0]
        docset = ca.select_one(f'.{HIERARCHY[0]}').text
        document = ca.select_one('.document')

        value_row = [docset, '', '', '', '', '', '', '', '', '', '', '']

        with open(f'./data/csv/{file_name}.csv', 'w', encoding='utf-8') as f:
            f.write('')

        if document is not None:
            for element in document:
                if isinstance(element, Tag):
                    classes = element.get('class')
                    if classes is not None:
                        for h in HIERARCHY:
                            if h in classes:
                                level = HIERARCHY.index(h)
                                if h == 'para':
                                    # Here, we have to check for nested elements!
                                    title_element = Bs(element.__str__(), 'html.parser').select_one(f'.{HEADING_DICT[h]}')
                                    title = title_element.text.replace('\n', '\t').replace('\t\t', '\t').replace('	', ' ').strip()
                                    text_content = []
                                    for c in element.contents:
                                        if isinstance(c, NavigableString):
                                            text_content.append(c)
                                        if isinstance(c, Tag):
                                            content_classes = c.get('class')
                                            if content_classes is not None:
                                                found = False
                                                for cl in content_classes:
                                                    if cl in HIERARCHY or cl in HEADING_LIST:
                                                        found = True
                                                if not found:
                                                    s = c.text.strip()
                                                    if len(s) > 0:
                                                        text_content.append(s)
                                            else:
                                                s = c.text.strip()
                                                if len(s) > 0:
                                                    text_content.append(s)

                                    if len(text_content) > 0:
                                        elem_text = ''.join(text_content).strip()
                                        if len(elem_text) > 0:
                                            text = title + '###SEP###' + elem_text
                                        else:
                                            text = title
                                    else:
                                        text = title

                                    text = text.replace('"', '""')

                                    value_row[level] = text
                                    handle_nested_node(element, value_row.copy(), 4, file_name)
                                else:
                                    title = Bs(element.__str__(), 'html.parser').select_one(f'.{HEADING_DICT[h]}').text.replace('\n', '\t').replace('\t\t', '\t').replace('	', ' ').strip()
                                    title = title.replace('"', '""')
                                    value_row[level] = title
