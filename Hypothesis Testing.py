# coding: utf-8

#
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
#

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import ttest_ind

# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
#
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
#
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
#
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
#
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.


# ---------------------------------------------------------------------------------------------------------------------------------------------------

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National',
          'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana',
          'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho',
          'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan',
          'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico',
          'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa',
          'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana',
          'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California',
          'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island',
          'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia',
          'ND': 'North Dakota', 'VA': 'Virginia'}


def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ],
    columns=["State", "RegionName"]  )

    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''

    global utdf
    utdf = pd.read_fwf('university_towns.txt', header=None)  # open the file and avoid the first row to be an index
    utdf['State'] = utdf[utdf[0].str.contains(
        "edit")]  # create a new column called State containing the rows strings where is contained the word "edit"
    utdf.columns = ['RegionName', 'State']  # rename the columns
    utdf['RegionName'] = utdf['RegionName'].str.replace("\s*\(.*\\s*",
                                                        '')  # delete () and everything in between in column region
    utdf['State'] = utdf['State'].str.replace("\s*\[.*\\s*",
                                              '')  # delete [] and everything in between in column country
    utdf['State'] = utdf['State'].fillna(method='ffill')  # fill the NaN with the word just above it in the column state
    utdf = utdf[~utdf.RegionName.str.contains("edit")]  # remove the rows that contains the word 'edit'
    utdf['RegionName'] = utdf['RegionName'].str.replace("\s*\[.*\]\s*",
                                                        '')  # delete [] and everything in between in column region
    utdf = utdf[['State', 'RegionName']]  # change the order of the columns
    print('\nANSWER 1:\n', utdf)


get_list_of_university_towns()


def get_recession_start():
    '''Returns the year and quarter of the recession start time as a
    string value in a format such as 2005q3'''

    '''From Bureau of Economic Analysis, US Department of Commerce, the GDP over time of the United States in current dollars 
    (use the chained value in 2009 dollars), in quarterly intervals, in the file gdplev.xls. 
    For this assignment, only look at GDP data from the first quarter of 2000 onward.'''

    gdp = pd.read_excel('gdplev.xls', skiprows=7)  # open file and delete first 7 rows
    gdp = gdp.drop(['Unnamed: 3', 'Unnamed: 7'], axis=1)  # delete columns
    gdp.columns = (['Current-Dollar and Real GDP Annual', 'GDP in billions of current dollars #1',
                    'GDP in billions of chained 2009 dollars #1', 'Quarterly (Seasonally adjusted annual rates)',
                    'GDP in billions of current dollars #2',
                    'GDP in billions of chained 2009 dollars #2'])  # rename columns

    gdp_start = gdp.loc[gdp['Quarterly (Seasonally adjusted annual rates)'] == '2000q1'].index[
        0]  # finds the index where the quarterly is 2000q1

    for x in range(gdp_start, len(gdp)):  # find 2 consequtive quarters where the GDP was decreasing
        if (gdp['GDP in billions of chained 2009 dollars #2'].iloc[x]) > (
        gdp['GDP in billions of chained 2009 dollars #2'].iloc[x + 1]) and (
        gdp['GDP in billions of chained 2009 dollars #2'].iloc[x + 1]) > (
        gdp['GDP in billions of chained 2009 dollars #2'].iloc[x + 2]):
            answer_2 = gdp['Quarterly (Seasonally adjusted annual rates)'].iloc[x + 1]
            print('\nANSWER 2:', answer_2)
            global recession_start  # creates a global variable that will be used in the function_ run_ttest()
            recession_start = answer_2
            break


get_recession_start()


def get_recession_end():
    '''Returns the year and quarter of the recession end time as a
    string value in a format such as 2005q3'''

    gdp = pd.read_excel('gdplev.xls', skiprows=7)  # open file and delete first 7 rows
    gdp = gdp.drop(['Unnamed: 3', 'Unnamed: 7'], axis=1)  # delete columns
    gdp.columns = (['Current-Dollar and Real GDP Annual', 'GDP in billions of current dollars #1',
                    'GDP in billions of chained 2009 dollars #1', 'Quarterly (Seasonally adjusted annual rates)',
                    'GDP in billions of current dollars #2',
                    'GDP in billions of chained 2009 dollars #2'])  # rename columns

    gdp_start = gdp.loc[gdp['Quarterly (Seasonally adjusted annual rates)'] == '2008q3'].index[
        0]  # finds the index where the quarterly is 2008q3 which is the year when the recession started

    for x in range(gdp_start, len(gdp)):  # find 2 consequtive quarters where the GDP was increasing
        if (gdp['GDP in billions of chained 2009 dollars #2'].iloc[x + 1]) > (
        gdp['GDP in billions of chained 2009 dollars #2'].iloc[x]) and (
        gdp['GDP in billions of chained 2009 dollars #2'].iloc[x + 2]) > (
        gdp['GDP in billions of chained 2009 dollars #2'].iloc[x + 1]):
            answer_3 = gdp['Quarterly (Seasonally adjusted annual rates)'].iloc[x + 2]
            print('\nANSWER 3:', answer_3)
            return


get_recession_end()


def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a
    string value in a format such as 2005q3'''

    gdp = pd.read_excel('gdplev.xls', skiprows=7)  # open file and delete first 7 rows
    gdp = gdp.drop(['Unnamed: 3', 'Unnamed: 7'], axis=1)  # delete columns
    gdp.columns = (['Current-Dollar and Real GDP Annual', 'GDP in billions of current dollars #1',
                    'GDP in billions of chained 2009 dollars #1', 'Quarterly (Seasonally adjusted annual rates)',
                    'GDP in billions of current dollars #2',
                    'GDP in billions of chained 2009 dollars #2'])  # rename columns

    gdp_start = gdp.loc[gdp['Quarterly (Seasonally adjusted annual rates)'] == '2008q3'].index[
        0]  # finds the index where the quarterly is 2008q3 which is the year when the recession started
    gdp_end = gdp.loc[gdp['Quarterly (Seasonally adjusted annual rates)'] == '2009q4'].index[
        0]  # finds the index where the quarterly is 2009q4 which is the year when the recession ended

    global gdp_min  # creates a global variable that will be used in the function_ run_ttest()
    gdp_min_index = gdp['GDP in billions of chained 2009 dollars #2'].loc[
                    gdp_start:gdp_end].idxmin()  # returns the index of the recession bottom
    gdp_min = gdp['Quarterly (Seasonally adjusted annual rates)'].loc[gdp_min_index]
    answer_4 = gdp_min
    print('\nANSWER 4:', answer_4)


get_recession_bottom()


def convert_housing_data_to_quarters():
    '''Converts the housing data (City_Zhvi_AllHomes.csv) to quarters
    and returns it as mean values in a dataframe. This dataframe
    should be a dataframe with columns for 2000q1 through 2016q3,
    and should have a multi-index in the shape of ["State","RegionName"].

    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.

    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    # use of the dictionary
    states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National',
              'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana',
              'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho',
              'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan',
              'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi',
              'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota',
              'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut',
              'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York',
              'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado',
              'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota',
              'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia',
              'ND': 'North Dakota', 'VA': 'Virginia'}
    hdf_states = pd.DataFrame([states]).T  # creates a list from the dictionary and transposes it

    # creates a new dataframe
    hdf = pd.read_csv('City_Zhvi_AllHomes.csv')
    hdf_full = pd.read_csv('City_Zhvi_AllHomes.csv')
    pd.set_option('display.max_columns', 500)
    hdf = hdf.drop(hdf.columns[6:51], axis=1)  # deletes columns from 1996-04 to 1999-12
    hdf_counter = len(hdf.columns)  # finds the number of columns from 2000-01 until the end
    hdf = hdf.iloc[:, 6:].groupby([i // 3 for i in range(6, hdf_counter)], axis=1).mean()

    quarter = []
    n = 0
    for i in range(2000,
                   2017):  # loop for creating the labels with increasing year (from 2000 to 2016) and quarters going from 1 to 4
        if i < 2016:
            for x in range(1, 5):
                n = n + 1
                quarter.append('{}q{}'.format(i, x))
        else:  # the else is created for the last year which has less quarters (only 3 rather than 4)
            for x in range(1, 4):
                n = n + 1
                quarter.append('{}q{}'.format(i, x))

    hdf.columns = (quarter)  # rename the columns of the excract of full hdf dataframe
    global hdf_merged  # declare the variable/df hdf_merged as a global variable that can be used in the next function
    hdf_merged = (
        pd.merge(pd.merge(hdf_full, hdf, left_index=True, right_index=True), hdf_states, how='inner', left_on='State',
                 right_index=True))  # it merges the extract of the full dataframe (with the new labels) with the full dataframe and with the dictionary dataframe
    hdf_merged.rename(columns={hdf_merged.columns[-1]: 'State', 'State': 'acr'},
                      inplace=True)  # change the labels of the columns (Last one coming from the dictionay into 'State' and 'State' into 'acr')
    hdf_merged = hdf_merged.set_index(['State', 'RegionName'])  # creates 2 index columns
    hdf_merged = hdf_merged.drop(hdf_merged.columns[0:250], axis=1)  # drops columns
    answer_5 = hdf_merged

    print('\nANSWER 5: Dataframe columns name\n', answer_5.columns)
    print('\nANSWER 5: Dataframe shape', answer_5.shape)


convert_housing_data_to_quarters()


def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values,
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence.

    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''

    hdf_merged['ratio'] = hdf_merged[gdp_min] / hdf_merged[recession_start]  # Creates a new column ratio
    housing_prices_recession = hdf_merged[[recession_start, gdp_min,
                                           'ratio']]  # Selects only the columns when the recession starts (in this case 2008q3) and when it reaches the bottom (in this case 2009q2)
    housing_prices_recession.reset_index(inplace=True)

    univ_cities = (pd.merge(utdf, housing_prices_recession, how='left', left_on=['RegionName', 'State'],
                            right_on=['RegionName',
                                      'State']))  # dataframe of house prices containing only university cities

    common = pd.merge(utdf, housing_prices_recession, on=['RegionName',
                                                          'State'])  # dataframe of house prices containing cities in common in between 2 dataframes
    not_univ = housing_prices_recession.sort_values(['State', 'RegionName'],
                                                    ascending=True)  # creates a new database of house prices containing both not univ cities and cities in common

    # algorithm to delete cities in 'common' database from 'not_univ' database.
    not_univ['key1'] = 1  # This df contains both not-univ cities and in common (10730 cities)
    common['key2'] = 1  # This df contains cities in common (269 cities)
    not_univ = pd.merge(not_univ, common, on=['RegionName', 'State'],
                        how='left')  # left outer join. Uses keys from left frame only
    not_univ = not_univ[~(
                not_univ.key2 == not_univ.key1)]  # it removes the lines where the cities are in common (where key1 and key2 are equal)
    # so the df contains not-univ cities not including the one in common (10461 cities)

    not_univ = not_univ.drop(['key1', 'key2', '2008q3_y', '2009q2_y', 'ratio_y'],
                             axis=1)  # drops columns from not_univ database
    not_univ.columns = ['State', 'RegionName', '2008q3', '2009q2', 'ratio']  # rename columns

    not_univ = not_univ.dropna(subset=['ratio'])  # drops rows having NaN values in the column 'ratio'
    univ_cities = univ_cities.dropna(subset=['ratio'])  # drops rows having NaN values in the column 'ratio'
    not_univ['2008q3/2009q2'] = (not_univ['2008q3'] / not_univ[
        '2009q2'])  # calculates the ratio in between not_univ cities columns 2008q3 and 2009q2
    univ_cities['2008q3/2009q2'] = (univ_cities['2008q3'] / univ_cities[
        '2009q2'])  # calculates the ratio in between_univ_cities columns 2008q3 and 2009q2
    ttest = stats.ttest_ind(univ_cities['2008q3/2009q2'],
                            not_univ['2008q3/2009q2'])  # calculates the ttest in the 2 columns

    if ttest[1] < 0.01:
        different = True
    else:
        different = False

    if not_univ['2008q3/2009q2'].mean() > univ_cities['2008q3/2009q2'].mean():
        better = ('university town')
    else:
        better = ('non-university town')

    print('\nANSWER 6: \nt-test at p<0.01 (true/false):',different,'\nt-test value:',ttest[1],'\nBetter university town or non-university towns:',better)

run_ttest()