from bs4 import BeautifulSoup as Bs, NavigableString, Tag
from tqdm import tqdm
from os import remove
from os.path import exists
from LOntoCA.util.constants import TO_BE_DELETED, URLConfig, ParseConfig, PathConfig
from pandas import read_csv
from pandas.errors import EmptyDataError
from glob import glob
import requests
import re


class DataManager:

    @staticmethod
    def download():
        # URL to database of collective agreements
        website = requests.get(url=URLConfig.CA_DATABASE_BASE_URL)

        # Extract all URLs to the collective agreements
        ca_list = re.findall(ParseConfig.CA_LINK_REGEX, str(website.content))

        # Iterate over all of those URLs
        for link in tqdm(ca_list):

            # Visit page of the corresponding collective agreement
            url = URLConfig.CA_BASE_URL + link
            ca_page = link[4:]  # Remove '/kv/' from the link
            website = requests.get(url=url)
            soup = Bs(website.content, ParseConfig.HTMLPARSER)

            # One page can have multiple documents. Find out, which document the current page shows
            active_element = soup.find_all('li', {'class': 'active'})
            if len(active_element) > 0:
                current_document = active_element[0].text

                # Check if there are other related documents and if so, get these related documents
                related_documents_parent = soup.find('ol', {'class': ParseConfig.RELATED_DOCUMENTS})
                related_documents = related_documents_parent.findChildren('li', recursive=False)
                current_element = active_element[0]
                if len(related_documents) > 2:
                    valid_element = True

                    # Iterate over the related documents until the 'real' (important) collective agreement appears
                    while 'Rahmen' not in current_document:
                        current_element = current_element.find_next('li')

                        # If we run out of related documents, there is no such collective agreement. We stop the process
                        if current_element is None:
                            valid_element = False
                            break

                    # If we found the CA we were looking for, we visit its page and download it
                    if valid_element:
                        link_to_detailed_page = current_element.find_next('a')['href']
                        url = URLConfig.CA_BASE_URL + str(link_to_detailed_page)
                        website = requests.get(url=url)
                        with open(PathConfig.get_file_path(file_name=ca_page, file_type='html'), 'wb') as f:
                            f.write(website.content)
                else:
                    if 'Rahmen' in current_document:
                        with open(PathConfig.get_file_path(file_name=ca_page, file_type='html'), 'wb') as f:
                            f.write(website.content)

    @staticmethod
    def _replace_class(soup: Bs, to_be_replaced: str, new_class_name: str):
        for el in soup.select(to_be_replaced):
            el['class'] = new_class_name

    @staticmethod
    def preprocess():
        # Remove collective agreements that don't exist anymore or have an invalid HTML structure
        print('Removing problematic files...')
        for f in tqdm(TO_BE_DELETED):
            if exists(f):
                remove(f)

        # Remove standing orders (Dienstordnungen)
        print('Removing standing orders...')
        for do in tqdm(glob(PathConfig.STANDING_ORDERS_WILDCARD)):
            remove(do)

        # The resulting HTML files contain a lot of empty rows that are deleted by this code
        # Note: The data itself is not changed in this step
        print("Reformat files...")
        for file in tqdm(glob(f'{PathConfig.HTML_DIR}*')):

            # Store file contents temporarily
            with open(file, 'r', encoding=ParseConfig.ENCODING) as f:
                lines = [i for i in f.readlines() if i and not i.isspace()]  # Remove empty lines

            # Reduce variability of HTML classes
            soup = Bs(''.join(lines), ParseConfig.HTMLPARSER)
            DataManager._replace_class(soup=soup, to_be_replaced=ParseConfig.ABS_GR_DIST, new_class_name='abs_gr')
            DataManager._replace_class(soup=soup, to_be_replaced=ParseConfig.ABSATZ_LITGR, new_class_name='absatz')

            # Store file with new HTML tags and no empty lines
            with open(file, 'w', encoding=ParseConfig.ENCODING) as f:
                f.write(str(soup))

    @staticmethod
    def transform_data():
        for file in tqdm(glob(f'{PathConfig.CSV_DIR}{PathConfig.CA_PREFIX}*')):
            try:
                file_name = file.split('\\')[-1].split('.')[0]

                # Iterate over rows in a csv file
                df = read_csv(file, encoding=ParseConfig.ENCODING, sep=',', header=None)
                for index, row in df.iterrows():

                    docset = row.iloc[0]                # The first col contains the docset name
                    doc_name = row.iloc[1]              # The second col contains the document name
                    section_name = row.iloc[2]          # The third col contains the section's name
                    cols_of_interest = row.iloc[3:]     # All columns after that depend on the file specific structure

                    # Remove columns that are empty and thus of type float
                    cols_of_interest = [c for c in cols_of_interest if c is not None and not isinstance(c, float) and len(c) > 0]

                    title_path = []     # List to construct title path e.g. § 8 > Abs 1 > ...
                    text_path = []      # List to construct the text path e.g. [§ 8] Rule 8 [Abs 1] Absatz 1
                    final_text = ''     # Text path as a string

                    for col in cols_of_interest:
                        final_text = ''  # Reset

                        # There are separators ###SEP### to distinguish between title and text
                        if ParseConfig.SEP in col:
                            parts = col.split(ParseConfig.SEP)
                            col_title = parts[0]
                            col_text = parts[1]

                        # If there's no separator, the clause does not have a text (just a title)
                        else:
                            col_title = col
                            col_text = ''

                        # A title can also indicate that the text is a table
                        if col_title == ParseConfig.TABELLEN_WRAPPER:
                            col_title = ParseConfig.TABELLE

                        # Append the variables to the path
                        title_path.append(col_title)
                        text_path.append(col_text)

                        # Construct the text path [title1] text1 [title1.a] text1.a ...
                        for ti, te in zip(title_path, text_path):
                            if len(te) > 0:
                                final_text += f'[{ti}] {te} '

                    # § 8 > Abs 1 > Lit b
                    title = ' > '.join(title_path)

                    # Escape double quotes for a correct representation in the csv file
                    title = title.replace('"', '""')
                    final_text = final_text.replace('"', '""')
                    doc_name = doc_name.replace('"', '""') if isinstance(doc_name, str) else doc_name
                    section_name = section_name.replace('"', '""') if isinstance(section_name, str) else section_name

                    # Only write the clause as a line if it has content
                    if len(title) > 0 or len(final_text) > 0:
                        with open(f'{PathConfig.FINAL_CSV_DIR}{file_name}.csv', 'a', encoding=ParseConfig.ENCODING) as f:
                            f.write(f'"{docset}","{doc_name}","{section_name}","{title}","{final_text}"\n')

            # We might encounter if the data has not been preprocessed since some CAs are invalid
            except EmptyDataError:
                file_name = file.split('\\')[-1].split('.')[0]
                print(f'{file_name}: EMPTY')

    @staticmethod
    def _transform_title(title: str):
        return title.replace('\n', '\t').replace('\t\t', '\t').replace('	', ' ').strip()

    @staticmethod
    def _handle_nested_node(element, value_row, index, file_name):
        has_relevant_children = False
        for content in element.contents:
            if isinstance(content, Tag):
                classes = content.get('class')
                if classes is not None:
                    for n in ParseConfig.HIERARCHY:
                        if n in classes:
                            has_relevant_children = True
                            '''
                            The class 'lit_gr_dist' appears in some cases and has no further meaning. Thus, we simply
                            skip it by calling the method on itself but not going down in the hierarchy.
                            '''
                            if not n == 'lit_gr_dist':
                                # We need to check if this hierarchy usually has a numbering and a heading or not
                                if isinstance(ParseConfig.HEADING_DICT[n], list):
                                    bs_element = Bs(content.__str__(), ParseConfig.HTMLPARSER)

                                    # nr is the numbering (e.g. Absatz 1 -> nr = 1)
                                    # title is the heading (e.g. Absatz 1 Sonderzahlungen -> Sonderzahlungen)
                                    nr = bs_element.select_one(f'.{ParseConfig.HEADING_DICT[n][0]}').text.strip()
                                    title_element = bs_element.select_one(f'.{ParseConfig.HEADING_DICT[n][1]}')

                                    # In case there is no heading, simply use the number
                                    if title_element is None:
                                        title = nr
                                    else:
                                        title = nr + DataManager._transform_title(title_element.text)

                                # Here, elements just have a title
                                else:
                                    # Skip hierarchy levels that don't have a title
                                    if ParseConfig.HEADING_DICT[n] != '':
                                        soup = Bs(content.__str__(), ParseConfig.HTMLPARSER)
                                        title_element = soup.select_one(f'.{ParseConfig.HEADING_DICT[n]}')
                                        if title_element is not None:
                                            title = DataManager._transform_title(title_element.text)
                                        else:
                                            title = 'Not Found'  # In case there is no title (or it has a wrong tag)
                                    else:
                                        title = n

                                # Special case: 'lit_text_liste' class, it contains <li> elements in a <ul> element
                                # -> We need to skip the <ul> element, otherwise the <li> elements can't be found
                                if n == ParseConfig.LIT_TEXT_LISTE:
                                    ul = content.find('ul')
                                    if ul is not None:
                                        # inside this class, <li> elements have a wrong class ('grey')
                                        wrong_label_elements = ul.find_all('li', {'class': 'grey'})
                                        for el in wrong_label_elements:
                                            el['class'] = 'intended_list'  # assign correct class

                                        # Go through child-elements
                                        n_contents = len(content.contents)
                                        cs = content.contents
                                        for i in range(n_contents):
                                            if isinstance(cs[i], Tag):
                                                if cs[i].name == 'ul':  # If the <ul> element is encountered
                                                    cs[i:i+1] = wrong_label_elements  # replace it with <li> elements

                                    # If there's no <ul> tag, there can be a <div> tag which does not comply with the
                                    # predefined hierarchy. Simply extract its text content.
                                    else:
                                        n_contents = len(content.contents)
                                        cs = content.contents
                                        for i in range(n_contents):
                                            if isinstance(cs[i], Tag):
                                                if cs[i].name == 'div' and cs[i].get('class') is None:
                                                    cs[i] = NavigableString(cs[i].text)

                                # Special case: HTML table -> store table as text
                                if not n == ParseConfig.TABELLEN_WRAPPER:
                                    text_content = []
                                    for c in content.contents:
                                        if isinstance(c, NavigableString):
                                            text_content.append(c)
                                        if isinstance(c, Tag):
                                            content_classes = c.get('class')
                                            if content_classes is not None:
                                                found = False
                                                for cl in content_classes:
                                                    if cl in ParseConfig.HIERARCHY or cl in ParseConfig.HEADING_LIST:
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
                                            text = title + ParseConfig.SEP + elem_text
                                        else:
                                            text = title
                                    else:
                                        text = title

                                else:
                                    # Escape double quotes for csv
                                    text = title + ParseConfig.SEP + str(content)

                                text = text.replace('"', '""').replace('\n', '\\n')

                                value_row[index] = text
                                DataManager._handle_nested_node(content, value_row.copy(), index+1, file_name)
                            else:
                                DataManager._handle_nested_node(content, value_row.copy(), index, file_name)

        if not has_relevant_children:
            with open(f'{PathConfig.CSV_DIR}{file_name}.csv', 'a', encoding=ParseConfig.ENCODING) as f:
                f.write(','.join([f'"{s}"' for s in value_row]) + '\n')

    @staticmethod
    def parse_files():
        for file in tqdm(glob(f'{PathConfig.HTML_DIR}{PathConfig.CA_PREFIX}*')):
            with open(file, 'r', encoding=ParseConfig.ENCODING) as f:
                ca = Bs(f.read(), ParseConfig.HTMLPARSER)
                file_name = file.split('\\')[-1].split('.')[0]

            # The docset name and the document element are always encoded the same way
            docset = ca.select_one(f'.{ParseConfig.HIERARCHY[0]}').text
            document = ca.select_one('.document')

            # Row to store the extracted hierarchies (e.g. kopf1-ve > kvgkopf > para > abs_gr > absatz
            value_row = [docset, '', '', '', '', '', '', '', '', '', '', '']

            # Clear file
            with open(f'{PathConfig.CSV_DIR}{file_name}.csv', 'w', encoding=ParseConfig.ENCODING) as f:
                f.write('')

            if document is not None:

                # Go through document elements (tags)
                for element in document:
                    if isinstance(element, Tag):
                        classes = element.get('class')
                        if classes is not None:
                            # Only consider elements that are part of the predefined hierarchy
                            for h in ParseConfig.HIERARCHY:
                                if h in classes:  # h is the level of the current element
                                    level = ParseConfig.HIERARCHY.index(h)
                                    if h == 'para':
                                        # Here, we have to check for nested elements!
                                        soup = Bs(element.__str__(), ParseConfig.HTMLPARSER)
                                        title_element = soup.select_one(f'.{ParseConfig.HEADING_DICT[h]}')
                                        title = DataManager._transform_title(title_element.text)
                                        text_content = []  # This list is for the NavigableStrings of that element
                                        for c in element.contents:
                                            if isinstance(c, NavigableString):
                                                text_content.append(c)
                                            if isinstance(c, Tag):
                                                # If we encounter a tag, we need to go in depth
                                                # We don't want to add text of children that are part of the hierarchy
                                                content_classes = c.get('class')
                                                if content_classes is not None:
                                                    found = False
                                                    for cl in content_classes:
                                                        # Check if we will see the element again
                                                        if cl in ParseConfig.HIERARCHY or cl in ParseConfig.HEADING_LIST:
                                                            found = True
                                                    # If not: add to text list
                                                    if not found:
                                                        s = c.text.strip()
                                                        if len(s) > 0:
                                                            text_content.append(s)
                                                else:
                                                    s = c.text.strip()
                                                    if len(s) > 0:
                                                        text_content.append(s)

                                        # Simply combine text if tag has text content
                                        if len(text_content) > 0:
                                            elem_text = ''.join(text_content).strip()
                                            # If clause has text and title, we put it together like title###SEP###text
                                            if len(elem_text) > 0:
                                                text = title + ParseConfig.SEP + elem_text
                                            else:
                                                text = title
                                        else:
                                            text = title

                                        # We again need to escape double quotes
                                        text = text.replace('"', '""')

                                        # Add the found information (title###SEP###text) to the right hierarchy index
                                        value_row[level] = text

                                        # Handle nested nodes (para might contain a div of class absatz)
                                        # Index denotes the hierarchy depth
                                        DataManager._handle_nested_node(element=element, value_row=value_row.copy(),
                                                                        index=4, file_name=file_name)

                                    # reaching this block means that the element is a title element (not para or lower)
                                    else:
                                        soup = Bs(element.__str__(), ParseConfig.HTMLPARSER)
                                        title_element = soup.select_one(f'.{ParseConfig.HEADING_DICT[h]}')
                                        title = DataManager._transform_title(title_element.text)

                                        # Escape double quotes
                                        title = title.replace('"', '""')

                                        # Simply save the title
                                        value_row[level] = title

    @staticmethod
    def clean():
        for f in tqdm(glob(f'{PathConfig.CSV_DIR}*.csv')):
            remove(f)




