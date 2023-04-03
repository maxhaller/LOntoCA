import os
from glob import glob
from bs4 import BeautifulSoup as Bs
from LOntoCA.util.constants import TO_BE_DELETED
from tqdm import tqdm


def preprocess():
    print('Removing problematic files...')

    # Remove collective agreements that don't exist anymore!
    for f in tqdm(TO_BE_DELETED):
        if os.path.exists(f):
            os.remove(f)

    # Remove Dienstordnungen
    for do in glob('./data/html/detail-do-*.html'):
        os.remove(do)

    print("Reformat files...")
    # The resulting HTML files contain a lot of empty rows that are deleted by this code
    for file in tqdm(glob('./data/html/*')):
        with open(file, 'r', encoding='utf-8') as f:
            lines = [i for i in f.readlines() if i and not i.isspace()]

        os.remove(file)

        with open(file, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        with open(file, 'r', encoding='utf-8') as f:
            soup = Bs(f.read(), 'html.parser')

        abs_dist_list = soup.select('.abs_gr_dist')
        for el in abs_dist_list:
            el['class'] = 'abs_gr'

        abs_litgr_list = soup.select('.absatz_litgr')
        for el in abs_litgr_list:
            el['class'] = 'absatz'

        with open(file, 'w', encoding='utf-8') as f:
            f.write(str(soup))
