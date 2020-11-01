def cleaning():
    with open("df_pickle_2020-10-28.okl", "rb", encoding="utf-8") as f:
        data = f.read()

    pattern = re.compile(r'PDFSEPERATOR')
    matches = pattern.finditer(data)

    df = pattern.split(data)
    df = pd.DataFrame(df)

    df.columns = ["text"]

    # Extracting case number and uncleaned date informatino from text
    df['case_number'] = df['text'].str.extract('(\w*?[№?].?\s*?[\w?\d?]*-\d*/\d*[.\w].?.?.?)', expand=True)
    df['date'] = df['text'].str.extract('(\d+[\s-][А-Яа-я]+ \d+.[А-Яа-я]+)', expand=True)

    # Cleaning out empty rows
    df.replace("", np.nan, inplace=True)
    df.dropna(subset=['text'], inplace=True)
    # df.replace(r'\\n',' ', regex=True, inplace = True)
    df.replace(r'\s', ' ', regex=True, inplace=True)
    df.reset_index(inplace=True)

    ### Extracting date information

    # Creating year and day variables
    df['year'] = df['date'].str.extract('(\d\d\d\d)', expand=True)
    df['day'] = df['date'].str.extract('(\d+(?<!\d\d\d\d)(?!\d))', expand=True)

    # Extracting months based on Kyrgyz and Russian language wording based on date column
    conditions = [df['date'].str.contains("янв"),
                  df['date'].str.contains("фев"),
                  df['date'].str.contains("март"),
                  df['date'].str.contains("апре"),
                  df['date'].str.contains(("мая|май")),
                  df['date'].str.contains("июн"),
                  df['date'].str.contains("июл"),
                  df['date'].str.contains("авг"),
                  df['date'].str.contains("сен"),
                  df['date'].str.contains("окт"),
                  df['date'].str.contains("ноя"),
                  df['date'].str.contains("дек")
                  ]
    # Define English language month values
    values = ['1',
              '2',
              '3',
              '4',
              '5',
              '6',
              '7',
              '8',
              '9',
              '10',
              '11',
              '12'
              ]
    # Create month column
    df['month'] = np.select(conditions, values)

    # Drop old date column
    df.drop(['date'], axis=1, inplace=True)

    # Create new date column
    df['date'] = pd.to_datetime(df[["year", "month", "day"]])

    ### Create type
    conditions = [df['text'].str.contains("(по\s+административным|административдик)", regex=True),
                  df['text'].str.contains("(по\s+уголовным|жазык\s+иштери)", regex=True),
                  df['text'].str.contains("(по\s+гражданским|жарандык\s+иштер|жарандык\s+жана\s+экономикалык\s+иштер)",
                                          regex=True),
                  ]
    # Define case types
    values = ['Administrative and economic',
              'Criminal',
              'Civil'
              ]
    # Create type column
    df['type'] = np.select(conditions, values)

    conditions = [df['text'].str.contains("(Республикасынын)", regex=True),
                  df['text'].str.contains("(Верховного)", regex=True)
                  ]
    # Define language values
    values = ['Kyrgyz',
              'Russian'
              ]
    # Create language column
    df['language'] = np.select(conditions, values)

    df.to_csv("dataset.csv")
