import pandas as pd
import numpy as np
import DataReader, Utils


class DataProcessor:
    processedDts = ''
    processedCensusDts = ''
    processedDates = []
    tc = 4

    drJHU = DataReader.DataReaderJHU()
    drCensusTSIdb5y = DataReader.DataReaderCensusTSIdb5y()
    drCensusACS1ySE = DataReader.DataReaderCensusACS1ySE()
    drGovernmentMeasures = DataReader.DataReaderGovernmentMeasures()
    drCensusACS5yP = DataReader.DataReaderCensusACS5yP()
    drInternationalBank = DataReader.DataReaderInternationalBank()
    drBrazilIO = DataReader.DataReaderBrazilIO()
    drIBGE = DataReader.DataReaderIBGE()

    result_path = 'Results/'

    def __init__(self):
        self.processedDates = self.drJHU.dateVector
        self.processedDts = self.drJHU.df

        self.processedCensusDts = pd.concat([self.drCensusTSIdb5y.df, self.drCensusACS1ySE.df])
        per_capita_dt = pd.concat([self.drCensusACS5yP.df, self.drInternationalBank.df])
        self.processedCensusDts = self.processedCensusDts.join(per_capita_dt)
        self.processedCensusDts = self.processedCensusDts.reset_index()

        self.processedCensusDts = self.processedCensusDts.append(self.drIBGE.df, ignore_index=True)

        self.processedCensusDts.loc[self.processedCensusDts['NAME'] == 'United States', 'NAME'] = 'US'

        for i in range(len(self.processedDts)):

            self.processedDts[i] = self.processedDts[i].loc[self.processedDts[i]['Country_Region'] != 'Brazil']
            append_brazil = self.drBrazilIO.df.loc[self.drBrazilIO.df['date'].dt.date == self.processedDates[i]]
            append_brazil = append_brazil[['Admin2', 'Province_State', 'Country_Region', 'Confirmed', 'Deaths',
                                           'Recovered']]
            self.processedDts[i] = self.processedDts[i].append(append_brazil, ignore_index=True)

            # Ver se vale a pena apagar o cruzeiro (Diamond Princess and Grand Princess rows) e o Vaticano do dataset
            # Falta informações das guianas, Martinique, St. Martin, Reunion, Channel Islands, Guadeloupe, Mayotte

            self.processedDts[i] = self.processedDts[i].replace(np.nan, 0)

            if i == 0:
                self.processedDts[i]['Rt'] = [1] * len(self.processedDts[i])
            else:
                dt_rt1 = self.processedDts[i][['Province_State', 'Country_Region', 'Confirmed', 'Deaths', 'Recovered']]
                province_country1 = dt_rt1['Province_State'] + dt_rt1['Country_Region']
                dt_rt1 = dt_rt1.assign(Province_Country=province_country1)
                active_cases1 = dt_rt1['Confirmed'] - dt_rt1['Deaths'] - dt_rt1['Recovered']
                dt_rt1 = dt_rt1.assign(Active=active_cases1)
                dt_rt1 = dt_rt1[['Province_Country', 'Active']].set_index('Province_Country')
                dt_rt2 = self.processedDts[i - 1][['Province_State', 'Country_Region', 'Confirmed', 'Deaths',
                                                   'Recovered']]
                province_country2 = dt_rt2['Province_State'] + dt_rt2['Country_Region']
                dt_rt2 = dt_rt2.assign(Province_Country=province_country2)
                active_cases2 = dt_rt2['Confirmed'] - dt_rt2['Deaths'] - dt_rt2['Recovered']
                dt_rt2 = dt_rt2.assign(Active=active_cases2)
                dt_rt2 = dt_rt2[['Province_Country', 'Active']].set_index('Province_Country')
                dt_rt = dt_rt1.join(dt_rt2, how='left', lsuffix='_current', rsuffix='_before')
                dt_rt['Rt'] = [1] * len(dt_rt)
                calculate_rt = (dt_rt['Active_before'] != np.nan) & (dt_rt['Active_before'] != 0)
                dt_rt.loc[calculate_rt, 'Rt'] += ((dt_rt.loc[calculate_rt, 'Active_current'] -
                                                   dt_rt.loc[calculate_rt, 'Active_before']) /
                                                  dt_rt.loc[calculate_rt, 'Active_before']) * self.tc
                dt_rt.reset_index(inplace=True)
                self.processedDts[i]['Rt'] = dt_rt['Rt'].copy()

                self.processedDts[i] = self.processedDts[i].replace(np.nan, 1)

    def plot_graph_country(self, data_type, country, per_million=False, brazil_registry=False):
        px = []
        py = []

        if per_million:
            div = 1000000
        else:
            div = 1

        plt_br_reg = brazil_registry and (country == 'Brazil')

        for i in range(len(self.processedDts)):
            # px.append(self.processedDates[i].strftime("%d/%m"))
            px.append(self.processedDates[i])

            country_dt = self.processedDts[i][self.processedDts[i]['Country_Region'] == country]
            if data_type != Utils.RT:
                if data_type == Utils.MORTALITY:
                    confirmed = country_dt[Utils.CONFIRMED].sum()
                    if confirmed != 0:
                        if plt_br_reg:
                            death_rows = self.drBrazilIO.deathRegistryDf.loc[
                                self.drBrazilIO.deathRegistryDf['date'].dt.date == self.processedDates[i]]
                        else:
                            death_rows = country_dt
                        py.append(death_rows[Utils.DEATHS].sum() / confirmed)
                    else:
                        py.append(0)
                elif plt_br_reg and data_type == Utils.DEATHS:
                    death_rows = self.drBrazilIO.deathRegistryDf.loc[
                        self.drBrazilIO.deathRegistryDf['date'].dt.date == self.processedDates[i]]
                    py.append((death_rows[[data_type]].sum()) / div)
                else:
                    py.append((country_dt[[data_type]].sum()) / div)
            else:
                size_cdt = len(country_dt)
                py.append(((country_dt[[data_type]].sum() - size_cdt) / size_cdt) + 1)

        return px, py

    def plot_graph_region(self, data_type, region, per_million=False, brazil_registry=False):
        px = []
        py = []

        if per_million:
            div = 1000000
        else:
            div = 1

        for i in range(len(self.processedDts)):
            # px.append(self.processedDates[i].strftime("%d/%m"))
            px.append(self.processedDates[i])

            region_dt = self.processedDts[i][self.processedDts[i]['Province_State'] == region]
            plt_br_reg = brazil_registry and len(region_dt['Country_Region'] == 'Brazil') > 0
            if data_type != Utils.RT:
                if data_type == Utils.MORTALITY:
                    confirmed = region_dt[Utils.CONFIRMED].sum()
                    if confirmed != 0:
                        if plt_br_reg:
                            death_rows = self.drBrazilIO.deathRegistryDf.loc[
                                 (self.drBrazilIO.deathRegistryDf['date'].dt.date == self.processedDates[i]) &
                                 (self.drBrazilIO.deathRegistryDf['Province_State'] == region)]
                        else:
                            death_rows = region_dt
                        py.append(death_rows[Utils.DEATHS].sum() / confirmed)
                    else:
                        py.append(0)
                elif data_type == Utils.DEATHS and plt_br_reg:
                    death_rows = self.drBrazilIO.deathRegistryDf.loc[
                        (self.drBrazilIO.deathRegistryDf['date'].dt.date == self.processedDates[i]) &
                        (self.drBrazilIO.deathRegistryDf['Province_State'] == region)]
                    py.append((death_rows[[data_type]].sum()) / div)
                else:
                    py.append((region_dt[[data_type]].sum()) / div)
            else:
                size_rdt = len(region_dt)
                py.append(((region_dt[[data_type]].sum() - size_rdt) / size_rdt) + 1)

        return px, py

    def country_names(self, order):
        countries = []

        if (order is None) or (order == Utils.ALPHABETICAL):
            for dt in self.processedDts:
                for _, row in dt.iterrows():
                    if row['Country_Region'] not in countries:
                        countries.append(row['Country_Region'])
            if order == Utils.ALPHABETICAL:
                countries.sort()
        elif order == Utils.PER_CAPITA_INCOME:
            for dt in self.processedDts:
                for _, row in dt.iterrows():
                    if not Utils.name_in_tuple_list(row['Country_Region'], countries):
                        row_census = self.processedCensusDts[self.processedCensusDts['NAME'] == row['Country_Region']]
                        row_census = ((row_census['PER_CAPITA_INCOME']).to_list())
                        if len(row_census) == 0:
                            row_census = [np.nan]
                        countries.append((row['Country_Region'], row_census[0]))
            countries.sort(key=Utils.take_second)
            countries, _ = list(zip(*countries))
        elif order == Utils.POPULATIONAL_DENSITY:
            for dt in self.processedDts:
                for _, row in dt.iterrows():
                    row_census = self.processedCensusDts[self.processedCensusDts['NAME'] == row['Country_Region']] \
                        .head(1)
                    if not Utils.name_in_tuple_list(row['Country_Region'], countries):
                        if (str(row_census['AREA_KM2']) != np.nan) and \
                                len(row_census['AREA_KM2'].tolist()) != 0 and \
                                (int(row_census['AREA_KM2'].tolist()[0]) != 0):
                            pop_density = row_census['POP'] / row_census['AREA_KM2']
                            pop_density = pop_density.tolist()
                        else:
                            pop_density = [np.nan]
                        countries.append((row['Country_Region'], pop_density[0]))
            countries.sort(key=Utils.take_second)
            countries, _ = list(zip(*countries))
        elif order == Utils.LARGER_RISK_GROUP:
            for dt in self.processedDts:
                for _, row in dt.iterrows():
                    row_census = self.processedCensusDts[self.processedCensusDts['NAME'] == row['Country_Region']] \
                        .head(1)
                    if not Utils.name_in_tuple_list(row['Country_Region'], countries):
                        if (str(row_census['POP']) != np.nan) and \
                                len(row_census['POP'].tolist()) != 0 and \
                                (int(row_census['POP'].tolist()[0]) != 0):
                            risk_group = row_census['POP60_99'] / row_census['POP']
                            risk_group = risk_group.tolist()
                        else:
                            risk_group = [np.nan]
                        countries.append((row['Country_Region'], risk_group[0]))
            countries.sort(key=Utils.take_second)
            countries, _ = list(zip(*countries))

        return countries

    def region_names(self, order, countries):
        regions = []

        if (order is None) or (order == Utils.ALPHABETICAL):
            for dt in self.processedDts:
                for _, row in dt.iterrows():
                    if (row['Province_State'] not in regions) and (row['Province_State'] != 'nan') \
                            and (row['Country_Region'] in countries):
                        regions.append(row['Province_State'])
            if order == Utils.ALPHABETICAL:
                regions.sort()
        elif order == Utils.PER_CAPITA_INCOME:
            for dt in self.processedDts:
                for _, row in dt.iterrows():
                    if (not Utils.name_in_tuple_list(row['Province_State'], regions)) and \
                            (row['Province_State'] != 'nan') and (row['Country_Region'] in countries):
                        row_census = self.processedCensusDts[self.processedCensusDts['NAME'] == row['Province_State']]
                        row_census = ((row_census['PER_CAPITA_INCOME']).to_list())
                        if len(row_census) == 0:
                            row_census = [np.nan]
                        regions.append((row['Province_State'], row_census[0]))
            regions.sort(key=Utils.take_second)
            regions, _ = list(zip(*regions))
        elif order == Utils.POPULATIONAL_DENSITY:
            for dt in self.processedDts:
                for _, row in dt.iterrows():
                    row_census = self.processedCensusDts[self.processedCensusDts['NAME'] == row['Province_State']] \
                        .head(1)
                    if (not Utils.name_in_tuple_list(row['Province_State'], regions)) and \
                            (row['Province_State'] != 'nan') and (row['Country_Region'] in countries):
                        if (str(row_census['AREA_KM2']) != np.nan) and \
                                len(row_census['AREA_KM2'].tolist()) != 0 and \
                                (int(row_census['AREA_KM2'].tolist()[0]) != 0):
                            pop_density = row_census['POP'] / row_census['AREA_KM2']
                            pop_density = pop_density.tolist()
                        else:
                            pop_density = [np.nan]
                        regions.append((row['Province_State'], pop_density[0]))
            regions.sort(key=Utils.take_second)
            regions, _ = list(zip(*regions))
        elif order == Utils.LARGER_RISK_GROUP:
            for dt in self.processedDts:
                for _, row in dt.iterrows():
                    row_census = self.processedCensusDts[self.processedCensusDts['NAME'] == row['Province_State']] \
                        .head(1)
                    if (not Utils.name_in_tuple_list(row['Province_State'], regions)) and \
                            (row['Province_State'] != 'nan') and (row['Country_Region'] in countries):
                        if (str(row_census['POP']) != np.nan) and \
                                len(row_census['POP'].tolist()) != 0 and \
                                (int(row_census['POP'].tolist()[0]) != 0):
                            risk_group = row_census['POP60_99'] / row_census['POP']
                            risk_group = risk_group.tolist()
                        else:
                            risk_group = [np.nan]
                        regions.append((row['Province_State'], risk_group[0]))
            regions.sort(key=Utils.take_second)
            regions, _ = list(zip(*regions))

        return regions

    def get_measure_types(self):
        categories = []
        measures = []

        for _, row in self.drGovernmentMeasures.df.iterrows():
            if row['CATEGORY'] not in categories:
                categories.append(row['CATEGORY'])
                measure = (self.drGovernmentMeasures.df[self.drGovernmentMeasures.df['CATEGORY']
                                                        == row['CATEGORY']])['MEASURE']
                measures.append(Utils.return_unique(measure.to_list()))

        return dict(zip(categories, measures))

    def plot_graph_government(self, country, measure_types):
        px = []
        py = []

        df = self.drGovernmentMeasures.df

        for i in range(len(self.processedDates)):
            # px.append(self.processedDates[i].strftime("%d/%m"))
            px.append(self.processedDates[i])
            py_value = 0
            # for measure_type in measure_types:
            py_value += len(df[(df['COUNTRY'] == country) & (df['MEASURE'].isin(measure_types)) &
                               (df['DELAYED_IMPACT'] <= np.datetime64(self.processedDates[i])) &
                               (df['LOG_TYPE'] == 'Introduction / extension of measures')])
            py_value -= len(df[(df['COUNTRY'] == country) & (df['MEASURE'].isin(measure_types)) &
                               (df['DELAYED_IMPACT'] <= np.datetime64(self.processedDates[i])) &
                               (df['LOG_TYPE'] == 'Phase-out measure')])

            py.append(py_value)

        return px, py

    def success_in_region(self, region, is_region):
        if is_region:
            look_in = 'Province_State'
        else:
            look_in = 'Country_Region'

        n_success = 0
        for dt in self.processedDts:
            if len(dt[(dt[look_in] == region) & (dt[Utils.RT] < 1)]) >= 1:
                n_success += 1
            elif n_success > 1:
                n_success -= 1

        return n_success >= self.drGovernmentMeasures.measures_delay

    def similar_country_measure(self, countries):
        similar_measures = set((self.drGovernmentMeasures.df[
            self.drGovernmentMeasures.df['COUNTRY'] == countries[0]])['MEASURE'])

        for i in range(1, len(countries)):
            gov_mes = (self.drGovernmentMeasures.df[self.drGovernmentMeasures.df['COUNTRY'] == countries[i]])['MEASURE']
            if len(gov_mes != 0):
                similar_measures = similar_measures.intersection(set(gov_mes))

        return list(similar_measures)

    def save_measures(self, countries, measures):
        save_df = self.drGovernmentMeasures.df[(self.drGovernmentMeasures.df['COUNTRY'].isin(countries)) &
                                               (self.drGovernmentMeasures.df['MEASURE'].isin(measures))]
        writer = pd.ExcelWriter(self.result_path + 'Gov_measures' + str(Utils.count_files(self.result_path)) + '.xlsx',
                                engine='xlsxwriter')
        save_df.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.save()

        # save_df.to_excel(self.result_path + 'Gov_measures' + str(Utils.count_files(self.result_path)) + '.xlsx',
        #                 index=False)
