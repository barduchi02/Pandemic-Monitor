# import DataProcessor
# import DataReader
# import pandas as pd
import Utils

# dr = DataReader.DataReaderBrazilIO()
# dr = DataReader.DataReaderIBGE()
# dr.print_full_data()

# dr = DataReader.DataReaderJHU()
# dr.print_full_data()

# dr = DataReader.DataReaderCensusACS1ySE()
# dr.print_full_data()

# dr = DataReader.DataReaderCensusTSIdb5y()
# dr.print_full_data()

# dr = DataReader.DataReaderGovernmentMeasures()
# dr.print_full_data()
# print(dr.df[['CATEGORY']])

# dp = DataProcessor.DataProcessor()
# print(dp)

# print(Utils.get_upper_case('Anumparava'))


def list_not_in_dataframe(list1, dataframe2):
    print('\n\n\n')
    for elem in list1:
        if len(dataframe2[dataframe2['NAME'] == elem]) == 0:
            print(elem)


def dataframe_not_in_list(list1, dataframe2):
    print('\n\n\n')
    for _, elem in dataframe2.iterrows():
        if str(elem['NAME']) not in list1:
            print(elem['NAME'])

