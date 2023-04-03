import pandas as pd
from glob import glob
from pandas.errors import EmptyDataError
from tqdm import tqdm

SEP = '###SEP###'


def transform_data():
    for file in tqdm(glob('./data/csv/detail-*')):
        try:
            file_name = file.split('\\')[-1].split('.')[0]

            with open(f'./data/final_csv/{file_name}.csv', 'w', encoding='utf-8') as f:
                f.write('')

            df = pd.read_csv(file, encoding='utf-8', sep=',', header=None)

            for index, row in df.iterrows():

                docset = row.iloc[0]
                doc_name = row.iloc[1]
                section_name = row.iloc[2]
                cols_of_interest = row.iloc[3:]
                cols_of_interest = [c for c in cols_of_interest if c is not None and not isinstance(c, float) and len(c) > 0]

                title_path = []
                text_path = []

                final_text = ''

                for col in cols_of_interest:

                    final_text = ''

                    if SEP in col:
                        parts = col.split(SEP)
                        col_title = parts[0]
                        col_text = parts[1]
                    else:
                        col_title = col
                        col_text = ''

                    if col_title == 'tabellen_wrapper':
                        col_title = 'tabelle'

                    title_path.append(col_title)
                    text_path.append(col_text)

                    for ti, te in zip(title_path, text_path):
                        if len(te) > 0:
                            final_text += f'[{ti}] {te} '

                title = ' > '.join(title_path)
                title = title.replace('"', '""')
                final_text = final_text.replace('"', '""')

                if isinstance(doc_name, str):
                    doc_name = doc_name.replace('"', '""')
                if isinstance(section_name, str):
                    section_name = section_name.replace('"', '""')

                if len(title) > 0 or len(final_text) > 0:
                    with open(f'./data/final_csv/{file_name}.csv', 'a', encoding='utf-8') as f:
                        f.write(f'"{docset}","{doc_name}","{section_name}","{title}","{final_text}"\n')
        except EmptyDataError:
            file_name = file.split('\\')[-1].split('.')[0]
            print(f'{file_name}: EMPTY')

