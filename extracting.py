import pdfplumber
import os
import concurrent.futures
from functools import wraps
import time
import pandas as pd
import pickle
from datetime import date


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
def extract_pdf(filename, directory):
    filename = os.fsdecode(filename)
    allpages_text = []
    data = []
    if filename.endswith('.pdf'):
        with pdfplumber.open(directory + filename) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                allpages_text.append(text)
            allpages_text = '-'.join(allpages_text)
            data.append(allpages_text)
            data.append(filename)

            return data


@timeit
def extract_all(directory):

    '''
    Uses extract_pdf to extract multiple PDFs within a directory.
    '''

    data = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:

        futures = {executor.submit(extract_pdf, filename, directory): filename for filename in os.listdir(directory)}

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                data.append(result)
            except Exception as exc:
                print("There was an error. It is defined as {}".format(exc))
    return data


@timeit
def extract_all_singleprocess(directory):
    return [extract_pdf(filename, directory) for filename in os.listdir(directory)]


if __name__ == '__main__':
    # filename = '224.pdf'
    directory = r'../files/' # r'C:/Users/peter/research_files/supreme_court/'

    results = extract_all(directory)
    with open(r'../data/pdfextracts_{}.pkl'.format(date.today()), 'wb') as file:
        pickle.dump(results, file)