from glob import glob
from os import remove
from tqdm import tqdm


def clean():
    for f in tqdm(glob('./data/html/*.csv')):
        remove(f)
