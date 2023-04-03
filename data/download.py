from bs4 import BeautifulSoup as bs
from tqdm import tqdm

import requests
import re


def download():
    # URL to database of collective agreements
    url = 'https://www.kollektivvertrag.at/cms/KV/KV_1.4/kollektivvertrag-suchen/alphabetische-liste'
    website = requests.get(url=url)

    # Extract all URLs to the collective agreements
    ca_list = re.findall(r'<a href="/kv/([a-zA-Z0-9-]+)">', str(website.content))
    kv = '/kv/'
    base_url = 'https://www.kollektivvertrag.at'

    # Iterate over all of those URLs
    for ca_page in tqdm(ca_list):

        # Visit page of the corresponding collective agreement
        url = base_url + kv + ca_page
        website = requests.get(url=url)
        soup = bs(website.content, 'html.parser')

        # One page can have multiple documents. Find out, which document the current page shows
        active_element = soup.find_all('li', {'class': 'active'})
        if len(active_element) > 0:
            current_document = active_element[0].text

            # Check if there are other related documents and if so, get these related documents
            related_documents_parent = soup.find('ol', {'class': 'related_documents'})
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
                    url = base_url + str(link_to_detailed_page)
                    website = requests.get(url=url)
                    with open(f'./data/html/detail-{ca_page}.html', 'wb') as f:
                        f.write(website.content)
            else:
                if 'Rahmen' in current_document:
                    with open(f'./data/html/detail-{ca_page}.html', 'wb') as f:
                        f.write(website.content)
