from bs4 import BeautifulSoup
import requests
import pickle
from datetime import date
import time
import re
from functools import wraps
import pandas as pd

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
def souping(court, act_type):

    '''
    :court Type of court
    :act_type Type of the document to be downloaded
    :return:
    '''

    url_list = []
    link_list = []
    data = []

    url = str('http://act.sot.kg/ru/search?caseno=&name=&articles=&court={}&judge=all&caseOpenedFrom=&caseType=all&actType={}&caseOpenedTo=&from=&to=&side1=&side2=&submit-act=%D0%90%D0%BA%D1%82%D1%8B&quantity=5000&page='.format(court, act_type))
               # SET QUANTITY TO APPROPRIATE LEVEL

    print('Finding out how many pages I need to look through.')

    soup = BeautifulSoup(requests.get(url).text, "html.parser")

    lastpage = soup.find("li", class_="last")
    lastpage = lastpage.find('a')['href']
    lastpage = int(re.search('\d*$', lastpage).group(0))
    lastpage += 1
    page_list = list(range(1, lastpage))  # For testing only, ENDVALUE should be lastpage

    print('I going to download information from {} pages'.format(lastpage))

    for i in page_list:
        url_list.append(url + str(i))

    for counter, url in enumerate(url_list, start=1):
        print('I am working on page {} of {}'.format(counter, lastpage-1))
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        table = soup.find('table')
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols_strip = []
            element = []
            links = []
            for ele in cols:
                cols_strip.append(ele.text.strip())
            for i in cols_strip:
                element.append(i)
            for ele in cols:
                link = ele.find('a')
                if link != None:
                    link = link.get('href')
                    links.append(link)
                    links_list = links
            element = element + links_list
            data.append(element)

    return data

if __name__ == '__main__':


    court = ""
    act_type = '2' # Постановление = 4 // Приговор = 2

    result = souping(court, act_type)

    with open(r'..\data\sotkg_data_acttype_{}_{}.pkl'.format(act_type, date.today()), 'wb') as file:
        pickle.dump(result, file)