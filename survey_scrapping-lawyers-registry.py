from docx import Document
import pickle
import pandas as pd
from datetime import date
import numpy as np
import urllib

url = 'http://minjust.gov.kg/upload/files/2017-07-21/9d165566b2ce38dc4a9d4d2b9b147cd6.docx'

file = urllib.request.urlretrieve(url)
document = Document(file)

tables = []
for table in document.tables:
    df = [['' for i in range(len(table.columns))] for j in range(len(table.rows))]
    for i, row in enumerate(table.rows):
        for j, cell in enumerate(row.cells):
            if cell.text:
                df[i][j] = cell.text
    tables.append(df)

    flat_list = []
for sublist in tables:
    for item in sublist:
        flat_list.append(item)

df = pd.DataFrame(flat_list)

### Preliminary cleaning

new_headers = df.iloc[1]
new_headers
df = df[2:]
df.columns = ['index', 'license_no', 'full_name', 'address', 'phone', 'decree', 'workplace', 'comment', 'empty1', 'empty2']
df.drop(['empty1', 'empty2'], axis = 1, inplace = True)

df.replace(r'\n',' ', regex=True, inplace = True)
df.replace(r'^\s*$', np.nan, regex=True, inplace = True)
df.dropna(subset = ['index', 'full_name'], how = "all", inplace = True)

with open('lawyers-{}.pkl'.format(date.today()), 'wb') as f:
    pickle.dump(df, f)