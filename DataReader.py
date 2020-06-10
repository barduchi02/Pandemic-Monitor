import urllib, requests
import pandas as pd
import numpy as np
import datetime
import Utils


class DataReader:
    url = ''
    df = ''

    CENSUS_BUREAU_KEY = 'd28ee389bc86b589cfaa01a013bffcfc28516b09'
    DATA_FOLDER = 'Data/'

    def print_full_data(self):
        print(self.df)

    def padronize_data(self):
        pass


class DataReaderJHU(DataReader):
    dateVector = []

    def __init__(self):
        self.url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data' \
                   '/csse_covid_19_daily_reports/'

        self.df = []
        date = datetime.date(2020, 1, 22)
        while True:
            file_name = date.strftime("%m-%d-%Y") + '.csv'
            file_url = self.DATA_FOLDER + file_name
            try:
                date = self.append_date(file_url, date)
            except OSError:
                try:
                    date = self.append_date(self.url + file_name, date)
                    self.df[-1].to_csv(file_url)
                except urllib.error.HTTPError:
                    break

        self.padronize_data()

    def append_date(self, url_full, date):
        self.df.append(pd.read_csv(url_full, error_bad_lines=False))
        self.dateVector.append(date)
        return date + datetime.timedelta(1)

    def padronize_data(self):

        for i in range(len(self.df)):
            if 'Province_State' not in self.df[i].columns:
                self.df[i].rename(columns={'Province/State': 'Province_State', 'Country/Region': 'Country_Region'},
                                  inplace=True)
            if 'Admin2' not in self.df[i].columns:
                self.df[i] = self.df[i].astype({'Province_State': str})
                adm2 = ['nan'] * self.df[i].shape[0]
                bool_array = Utils.string_in_tuple(',', self.df[i]['Province_State'], True)
                index, search = zip(*bool_array)
                index = list(index)
                search = list(search)
                adm_rows = self.df[i][search]
                for j, row in adm_rows.iterrows():
                    if row['Country_Region'] == 'US':
                        adm2[index[j]], state_name = Utils.string_until(row['Province_State'], ',')
                        self.df[i].loc[self.df[i]['Province_State'] ==
                                       adm2[index[j]] + ', ' + state_name, 'Province_State'] = \
                            Utils.state_names[state_name[0:2]]
                self.df[i].insert(0, 'Admin2', adm2, True)
            columns = ['Admin2', 'Province_State', 'Country_Region', 'Confirmed', 'Deaths', 'Recovered']
            self.df[i] = self.df[i][columns]
            self.df[i] = self.df[i].astype({'Admin2': str, 'Province_State': str, 'Country_Region': str,
                                            'Confirmed': float, 'Deaths': float, 'Recovered': float})

            self.df[i].loc[self.df[i]['Province_State'] == 'None', 'Province_State'] = 'nan'

            self.summarize_country('China', i, columns)
            self.summarize_country('Canada', i, columns)
            self.summarize_country('Australia', i, columns)
            self.summarize_country('Germany', i, columns)
            self.summarize_country('Iran', i, columns)
            self.summarize_country('Russia', i, columns)
            self.summarize_country('Moldova', i, columns)
            self.summarize_country('Taiwan', i, columns)

            self.summarize_us_states(i, columns)

            israel_total = self.df[i][(self.df[i]['Country_Region'] == 'Israel') | (self.df[i]['Country_Region'] ==
                                                                                    'Palestine') |
                                      (self.df[i]['Country_Region'] == 'occupied Palestinian territory') |
                                      (self.df[i]['Country_Region'] == 'West Bank and Gaza')]
            self.df[i].loc[self.df[i]['Country_Region'] == 'Israel', columns] = ['nan', 'nan', 'Israel',
                                                                                 israel_total['Confirmed'].sum(),
                                                                                 israel_total['Deaths'].sum(),
                                                                                 israel_total['Recovered'].sum()]
            self.df[i] = self.df[i].loc[(self.df[i]['Country_Region'] != 'Palestine') &
                                        (self.df[i]['Country_Region'] != 'occupied Palestinian territory') &
                                        (self.df[i]['Country_Region'] != 'West Bank and Gaza')]

            self.df[i].loc[self.df[i]['Country_Region'] == 'Republic of Korea', 'Country_Region'] = 'South Korea'
            self.df[i].loc[self.df[i]['Country_Region'] == 'Korea, South', 'Country_Region'] = 'South Korea'
            self.df[i].loc[self.df[i]['Country_Region'] == 'Viet Nam', 'Country_Region'] = 'Vietnam'
            self.df[i].loc[self.df[i]['Country_Region'] == 'Czech Republic', 'Country_Region'] = 'Czechia'
            self.df[i].loc[self.df[i]['Country_Region'] == 'Bahamas', 'Country_Region'] = 'The Bahamas'
            self.df[i].loc[self.df[i]['Country_Region'] == 'Gambia', 'Country_Region'] = 'The Gambia'
            self.df[i].loc[self.df[i]['Country_Region'] == 'Timor-Leste', 'Country_Region'] = 'East Timor'

            self.df[i].loc[self.df[i]['Country_Region'] == 'United Kingdom', 'Country_Region'] = 'UK'
            self.summarize_country('UK', i, columns)

            self.df[i].reset_index(inplace=True, drop=True)

    def summarize_country(self, country, i, columns):
        country_rows = self.df[i][Utils.string_in(country, self.df[i]['Country_Region'], True)]
        country_df = [['nan', 'nan', country, country_rows['Confirmed'].sum(), country_rows['Deaths'].sum(),
                       country_rows['Recovered'].sum()]]

        self.df[i] = self.df[i].loc[Utils.string_in(country, self.df[i]['Country_Region'], False)]
        self.df[i] = pd.concat([self.df[i], pd.DataFrame(country_df, columns=columns)])

    def summarize_us_states(self, i, columns):
        for us_states in Utils.state_names.values():
            us_rows = self.df[i].loc[self.df[i]['Province_State'] == us_states]
            us_states_df = [['nan', us_states, 'US', us_rows['Confirmed'].sum(), us_rows['Deaths'].sum(),
                             us_rows['Recovered'].sum()]]

            self.df[i] = self.df[i].loc[self.df[i]['Province_State'] != us_states]
            self.df[i] = pd.concat([self.df[i], pd.DataFrame(us_states_df, columns=columns)])


class DataReaderCensusTSIdb5y(DataReader):

    def __init__(self):
        # Time Series International Database: International Populations by 5 Year Age Groups and Sex
        # Found at https://api.census.gov/data.html
        self.url = 'https://api.census.gov/data/timeseries/idb/5year?get=FIPS,NAME,AREA_KM2,POP,POP60_64,POP65_69,' \
                   'POP70_74,POP75_79,POP80_84,POP85_89,POP90_94,POP95_99&time=2020&key=' + self.CENSUS_BUREAU_KEY
        data = requests.get(self.url).json()
        self.df = pd.DataFrame(data[1:], columns=data[0])
        self.padronize_data()

    def padronize_data(self):
        self.df['POP60_99'] = pd.to_numeric(self.df['POP60_64']) + pd.to_numeric(self.df['POP65_69']) + \
                              pd.to_numeric(self.df['POP70_74']) + pd.to_numeric(self.df['POP75_79']) + \
                              pd.to_numeric(self.df['POP80_84']) + pd.to_numeric(self.df['POP85_89']) + \
                              pd.to_numeric(self.df['POP90_94']) + pd.to_numeric(self.df['POP95_99'])
        self.df['POP'] = pd.to_numeric(self.df['POP'])
        self.df['AREA_KM2'] = pd.to_numeric(self.df['AREA_KM2'])

        self.df.loc[self.df['NAME'] == 'Timor-Leste', 'NAME'] = 'East Timor'
        self.df.loc[self.df['NAME'] == 'Virgin Islands, U.S.', 'NAME'] = 'United States Virgin Islands'

        country_rows = self.df[Utils.string_in(', ', self.df['NAME'], True)]
        for i, row in country_rows.iterrows():
            s1, s2 = Utils.string_until(row['NAME'], ',')
            self.df.at[i, 'NAME'] = s2 + ' ' + s1
        self.df = pd.concat([self.df[Utils.string_in(', ', self.df['NAME'], False)], country_rows])

        self.df = self.df[['NAME', 'POP', 'POP60_99', 'AREA_KM2']]

        self.df.loc[self.df['NAME'] == 'United Kingdom', 'NAME'] = 'UK'
        self.df.loc[self.df['NAME'] == 'Bahamas, The', 'NAME'] = 'The Bahamas'
        self.df = self.df.set_index('NAME')

    def summarize_country(self, country):
        country_rows = self.df[Utils.string_in(country, self.df['NAME'], True)]
        country_df = [[country, country_rows['POP'].sum(), country_rows['POP60_99'].sum(),
                       country_rows['AREA_KM2'].sum()]]
        self.df = self.df.loc[Utils.string_in(country, self.df['NAME'], False)]
        self.df = pd.concat([self.df, pd.DataFrame(country_df, columns=self.df.columns)])


class DataReaderCensusACS1ySE(DataReader):
    areaDf = ''

    def __init__(self):
        # ACS 1-Year Supplemental Estimates
        # Found at https://api.census.gov/data.html
        self.url = 'https://api.census.gov/data/2018/acs/acsse?get=NAME,K200104_001E,K200104_008E&for=state:*&key=' + \
                   self.CENSUS_BUREAU_KEY
        data = requests.get(self.url).json()
        data[0][1] = 'POP'
        data[0][2] = 'POP60_99'
        self.df = pd.DataFrame(data[1:], columns=data[0])

        # Area data can be found in https://www.census.gov/geographies/reference-files/2010/geo/state-area.html
        self.areaDf = pd.read_csv(self.DATA_FOLDER + 'US_Area_Data.csv', error_bad_lines=False)

        self.padronize_data()

    def padronize_data(self):
        self.df['POP'] = pd.to_numeric(self.df['POP'])
        self.df['POP60_99'] = pd.to_numeric(self.df['POP60_99'])
        self.df = self.df[['NAME', 'POP', 'POP60_99']]

        self.areaDf.rename(columns={'State and other areas2': 'NAME', 'Total Area (Sq. Km)': 'AREA_KM2'}, inplace=True)
        self.areaDf = self.areaDf[['NAME', 'AREA_KM2']]

        self.df = self.df.set_index('NAME').join(self.areaDf.set_index('NAME'))


class DataReaderCensusACS5yP(DataReader):

    def __init__(self):
        # ACS 5-Year Data Profiles
        # Found at https://api.census.gov/data.html
        self.url = 'https://api.census.gov/data/2018/acs/acs5/profile?get=NAME,DP03_0088E&for=state:*&key=' + \
                   self.CENSUS_BUREAU_KEY
        data = requests.get(self.url).json()
        data[0][1] = 'PER_CAPITA_INCOME'
        self.df = pd.DataFrame(data[1:], columns=data[0])

        self.padronize_data()

    def padronize_data(self):
        self.df['PER_CAPITA_INCOME'] = pd.to_numeric(self.df['PER_CAPITA_INCOME'])
        self.df = self.df[['NAME', 'PER_CAPITA_INCOME']]
        self.df.loc[self.df['NAME'] == 'Bahamas, The', 'NAME'] = 'The Bahamas'
        self.df.set_index('NAME', inplace=True)


class DataReaderInternationalBank(DataReader):

    def __init__(self):
        self.url = self.DATA_FOLDER + 'API_NY.GDP.PCAP.PP.CD_DS2_en_excel_v2_990699.xls'
        self.df = pd.read_excel(self.url, sheet_name=0)

        self.padronize_data()

    def padronize_data(self):
        self.df.rename(columns={'Country Name': 'NAME', '2018': 'PER_CAPITA_INCOME'}, inplace=True)
        self.df = self.df[['NAME', 'PER_CAPITA_INCOME']]
        self.df.set_index('NAME', inplace=True)


class DataReaderGovernmentMeasures(DataReader):
    measures_delay = 19

    def __init__(self):
        self.url = self.DATA_FOLDER + 'acaps_covid19_government_measures_dataset.xlsx'
        self.df = pd.read_excel(self.url, sheet_name=2)
        # self.url = \
        #    'https://www.acaps.org/sites/acaps/files/resources/files/acaps_covid19_goverment_measures_dataset.xlsx'
        # self.df = pd.read_excel(self.url, sheet_name=2)

        self.padronize_data()

    def padronize_data(self):
        self.df['DELAYED_IMPACT'] = self.df['DATE_IMPLEMENTED'] + datetime.timedelta(self.measures_delay)
        self.df = self.df[['COUNTRY', 'LOG_TYPE', 'CATEGORY', 'MEASURE', 'DELAYED_IMPACT', 'COMMENTS', 'LINK']]
        self.df.loc[self.df['COUNTRY'] == 'United Kingdom', 'COUNTRY'] = 'UK'
        self.df.loc[self.df['COUNTRY'] == 'United States of America', 'COUNTRY'] = 'US'
        self.df.loc[self.df['COUNTRY'] == 'Russian Federation', 'COUNTRY'] = 'Russia'
        self.df.loc[self.df['COUNTRY'] == 'Brunei Darussalam', 'COUNTRY'] = 'Brunei'
        self.df.loc[self.df['COUNTRY'] == 'Czech Republic', 'COUNTRY'] = 'Czechia'
        self.df.loc[self.df['COUNTRY'] == 'Korea Republic of', 'COUNTRY'] = 'South Korea'
        self.df.reset_index(inplace=True, drop=True)

        for index, gov_measure in self.df.iterrows():
            self.df.loc[index, 'MEASURE'] = Utils.get_upper_case(gov_measure['MEASURE'])


class DataReaderBrazilIO(DataReader):
    deathRegistryDf = ''
    deathRegistryUrl = ''

    averageRecoveryDays = 17
    daysToDeathRegistry = 14

    def __init__(self):
        self.url = 'https://brasil.io/api/dataset/covid19/caso_full/data?place_type=state'
        data_read = requests.get(self.url).json()
        self.df = pd.DataFrame.from_dict(data_read['results'])
        while data_read['next'] is not None:
            data_read = requests.get(data_read['next']).json()
            self.df = self.df.append(pd.DataFrame.from_dict(data_read['results']))

        self.deathRegistryUrl = 'https://brasil.io/api/dataset/covid19/obito_cartorio/data'
        data_read = requests.get(self.deathRegistryUrl).json()
        self.deathRegistryDf = pd.DataFrame.from_dict(data_read['results'])
        while data_read['next'] is not None:
            data_read = requests.get(data_read['next']).json()
            self.deathRegistryDf = self.deathRegistryDf.append(pd.DataFrame.from_dict(data_read['results']))

        self.padronize_data()

    def padronize_data(self):
        self.df.rename(columns={'state': 'Province_State', 'last_available_confirmed': 'Confirmed',
                                'last_available_deaths': 'Deaths'}, inplace=True)
        self.df = self.df[['date', 'Province_State', 'Confirmed', 'Deaths']]
        self.df = self.df.astype({'date': 'datetime64', 'Confirmed': 'int64', 'Deaths': 'int64'})
        self.df['Country_Region'] = ['Brazil'] * len(self.df)

        self.df.sort_values(by=['date', 'Province_State'], inplace=True, ignore_index=True)
        recovered = [0] * len(self.df)
        for i in range(0, len(recovered)):
            previous_confirmed = self.df.loc[(self.df['Province_State'] == self.df.iloc[i]['Province_State']) &
                                             (self.df['date'] ==
                                             (self.df.iloc[i]['date'] -
                                              pd.Timedelta(self.averageRecoveryDays, unit='d')))]
            if len(previous_confirmed) > 0:
                recovered[i] = int(previous_confirmed['Confirmed'] - self.df.iloc[i]['Deaths'])
        self.df['Recovered'] = recovered

        self.df['Admin2'] = ['nan'] * len(self.df)

        self.deathRegistryDf.replace(np.nan, 0, inplace=True)
        self.deathRegistryDf.replace('None', 0, inplace=True)
        self.deathRegistryDf = self.deathRegistryDf.astype({'date': 'datetime64'})
        self.deathRegistryDf['Deaths'] = self.deathRegistryDf['deaths_covid19'] + \
                                         self.deathRegistryDf['deaths_sars_2020']
        self.deathRegistryDf['date'] = self.deathRegistryDf['date'] + pd.Timedelta(self.daysToDeathRegistry, unit='d')
        self.deathRegistryDf.rename(columns={'state': 'Province_State'}, inplace=True)
        self.deathRegistryDf = self.deathRegistryDf[['date', 'Province_State', 'Deaths']]


class DataReaderIBGE(DataReader):
    area_url = ''
    per_capita_url = ''

    def __init__(self):

        self.area_url = \
            'https://servicodados.ibge.gov.br/api/v3/agregados/1301/periodos/2010/variaveis/615?localidades=N3[all]'
        data_read = requests.get(self.area_url).json()
        data_dict = {'NAME': [], 'AREA_KM2': []}
        for data in data_read[0]['resultados'][0]['series']:
            data_dict['NAME'].append(data['localidade']['nome'])
            data_dict['AREA_KM2'].append(data['serie']['2010'])
        self.df = pd.DataFrame.from_dict(data_dict)

        self.url = 'https://servicodados.ibge.gov.br/api/v3/agregados/2104/periodos/2010/variaveis/' \
                   '138?localidades=N3[all]&classificacao=133[0]|59[0]|58[0,3520,3244]'
        data_read = requests.get(self.url).json()
        self.df['POP'] = [0] * len(self.df)
        for data in data_read[0]['resultados'][0]['series']:
            self.df.loc[self.df['NAME'] == data['localidade']['nome'], 'POP'] = \
                float(data['serie']['2010'])
        self.df['POP60_99'] = [0] * len(self.df)
        for i in range(1, len(data_read[0]['resultados']) - 1):
            for data in data_read[0]['resultados'][i]['series']:
                self.df.loc[self.df['NAME'] == data['localidade']['nome'], 'POP60_99'] += \
                    float(data['serie']['2010'])

        self.per_capita_url = 'https://servicodados.ibge.gov.br/api/v3/agregados/3974/periodos/2010/variaveis/' \
                              '3948?localidades=N3[all]&classificacao=12085[100543]|58[95253]'
        data_read = requests.get(self.per_capita_url).json()
        self.df['PER_CAPITA_INCOME'] = [0] * len(self.df)
        for data in data_read[0]['resultados'][0]['series']:
            self.df.loc[self.df['NAME'] == data['localidade']['nome'], 'PER_CAPITA_INCOME'] = \
                float(data['serie']['2010'])

        self.padronize_data()


    def padronize_data(self):
        pass
