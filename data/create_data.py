from LOntoCA.util.DataManager import DataManager
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-ndo', '--no-download', help='Do not download the data',
                        action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('-npre', '--no-preprocess', help='Do not preprocess the data',
                        action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('-npar', '--no-parse', help='Do not parse the data',
                        action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('-ntr', '--no-transform', help='Do not transform the data',
                        action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('-ncl', '--no-clean', help='Do not remove temporary files',
                        action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()

    if not args.no_download:
        print('downloading collective agreements...')
        DataManager.download()
        print('download successful')

    if not args.no_preprocess:
        print('preprocessing...')
        DataManager.preprocess()
        print('data preprocessed successfully')

    if not args.no_parse:
        print('parsing data...')
        DataManager.parse_files()
        print('data parsed successfully')

    if not args.no_transform:
        print('transforming data...')
        DataManager.transform_data()
        print('data transformed successfully')

    if not args.no_clean:
        print('removing temporary csv files...')
        DataManager.clean()
        print('files removed')




