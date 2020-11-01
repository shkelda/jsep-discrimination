import os
import re
import urllib
from pathlib import Path
from urllib.request import urlretrieve
import pandas as pd
import pickle
import time
import concurrent.futures
from functools import wraps
from tqdm import tqdm

def timeit(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = method(*args, **kwargs)
        end_time = time.time()
        print(f"{method.__name__} => {(end_time-start_time)*1000} ms")

        return result

    return wrapper

@timeit
def downloading_one(url, directory):

    req = urllib.request.urlopen(url)
    fullpath = Path(url)
    fname = fullpath.name

        # Combine the name and the downloads directory to get the local filename
    download = os.path.join(directory, fname)

    # print('I am now attempting to download {}'.format(fname))
    if not os.path.isfile(download): # Do not download the file if it already exists in directory
        try:
            urlretrieve(url, download)
        except urllib.error.HTTPError as e:
            print(e.reason)

@timeit
def downloading_bulk_singleprocess(url_list):
    print('I will download {} files.'.format(len(url_list)))
    return [downloading_one(url, directory) for url in url_list]

@timeit
def downloading_bulk(url_list):
    '''
    This function uses download_one() to download a list of files with multi-threading.
    '''
    with tqdm(total=int(len(url_list))) as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(downloading_one, url, directory): url for url in url_list}
            results = {}
            for future in concurrent.futures.as_completed(futures):
                arg = futures[future]
                results[arg] = future.result()
                pbar.update(1)

if __name__ == '__main__':

    # url = 'http://act.sot.kg/act/download/190580.pdf'
    # url_list = ['http://act.sot.kg/act/download/68.pdf','http://act.sot.kg/act/download/70.pdf', 'http://act.sot.kg/act/download/83.pdf','http://act.sot.kg/act/download/94.pdf']
    directory = r'C:\Users\peter\Python\research_files\files'

    df = pd.read_pickle(r'../data/DF_acttype_4_2020-11-01.pkl')
    url_list = df['link_file'].tolist()

    downloading_bulk(url_list)