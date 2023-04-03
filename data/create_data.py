from download import download
from preprocess import preprocess
from parse_quickfix import parse_files
from transform import transform_data
from clean import clean

print('downloading collective agreements...')
download()
print('download successful')

print('preprocessing...')
preprocess()
print('data preprocessed successfully')

print('parsing data...')
parse_files()
print('data parsed successfully')

print('transforming data...')
transform_data()
print('data transformed successfully')

print('removing temporary csv files...')
clean()
print('files removed')
