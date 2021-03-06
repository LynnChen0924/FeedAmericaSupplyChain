# -*- coding: utf-8 -*-
"""
@author: Gorden Li
"""

import pandas as pd
import datetime as dt

#Import plot lib
import matplotlib.pyplot as plt
import seaborn as sns

#Import norm distribution check
from scipy import stats

#Import Numpy
import numpy as np

def readasdf(route):
    csv_file = route
    csv_data = pd.read_csv(csv_file, low_memory = False)
    df = pd.DataFrame(csv_data)
    df = df.loc[ : , ~df.columns.str.contains("^Unnamed")]
    return(df)

def addblankcol(df, index, colnamelist):
    for colname in colnamelist:
        df.insert(index, colname, '')
        index += 1
    return(df)

def monthtoseason(month):
    season = None
    if month <=3:
        season = 'Spring'
    elif month <= 6:
        season = 'Summer'
    elif month <= 9:
        season = 'Autumn'
    else:
        season = 'Winter'
    return season

#Set derived variables:
def findDieselprice(actual_date, pricedata):
    price = 0
    for row in range(len(pricedata)):
        if  pricedata.loc[row, 'Week'] - actual_date < dt.timedelta(days = 7):
            price = pricedata.loc[row, 'Retail Prices Dollars per Gallon']
            return price
        
#Abnormalization check
def Continuous_Feature_Abnorm_Analysis(Feature_list, k):
    for Feature in Feature_list:
        plt.figure()
        plt.subplot(1, 2, 1)
        sns.boxplot(y = data[Feature])
        
        q_low = data[Feature].quantile(q=0.25)
        q_high = data[Feature].quantile(q=0.75)
        q_interval = q_high - q_low
        index_high = data[Feature] <= (q_high + k * q_interval) #k use 1.5 or 3.0 as multiplier of q_interval
        index_low = data[Feature] >= (q_low - k * q_interval)
        print(index_high)

        print(Feature + " abnormal sample number：",len(data)-len(data[index_low & index_high]))
        plt.subplot(1, 2, 2)
        sns.boxplot(y=data[Feature][index_low & index_high])
        plt.show()
        #plt.show() is needed in every plot if we are to pic them onebyone instead of showing the last pic
         
def Discrete_Feature_Abnorm_Analysis(Feature_list):
    for Feature in Feature_list:
        print(data[Feature].value_counts())
        print('-----------------------------------------------')
        
#Distribution Analysis
def Distribution(Feature_list):
    for Feature in Feature_list:
        plt.figure()
        plt.title('skew: '+str(round(data[Feature].skew(), 2)) + '   ' + 'kurtosis: '+str(round(data[Feature].kurtosis(), 2)) + \
                  '\n' + 'KsTest: '+str(round(stats.kstest(data['Miles'], 'norm', (data['Miles'].mean(), data['Miles'].std()))[1], 2)))
        sns.distplot(data[Feature])
        #if KsTest P value <= 0.05, it does not obey normal distribution
        plt.show()
    
def Hist(Feature_list):
    for Feature in Feature_list:
        plt.figure()
        plt.title(Feature)
        plt.hist(data[Feature])
        plt.show()

def split_train_test(data, test_ratio):
    np.random.seed(1)
    
    shuffled_indices = np.random.permutation(len(data)) #generate a list of random with no replacement
    
    test_set_size = int(round(len(data) * test_ratio, 0))
    test_indices = shuffled_indices[:test_set_size]
    train_indices = shuffled_indices[test_set_size:]
    
    return data.iloc[train_indices], data.iloc[test_indices]   

#---------------------------------------------------------------------------------------------------------------------------------
data = readasdf('C:/Personal/Wustl-MSCA/Spring 2021/Data Analysist Competition/Competition data/Order_detail_summary---Cleaned Report3.csv')

#-----------------------------------------------------------------------------------------------------
###Setting derived variables
Diesel_price = readasdf('C:/Personal/Wustl-MSCA/Spring 2021/Data Analysist Competition/Competition data/Weekly_U.S._No_2_Diesel_Ultra_Low_Sulfur_(0-15_ppm)_Retail_Prices.csv')

Route_Density = readasdf('C:/Personal/Wustl-MSCA/Spring 2021/Data Analysist Competition/Competition data/American High Way Info By State.csv')
Route_Density_Dict = {Route_Density.loc[row, 'State']: list(Route_Density.iloc[row, 1:4]) for row in range(len(Route_Density))}

for row in range(len(Diesel_price)):
    Diesel_price.loc[row, 'Week'] = dt.datetime.strptime(Diesel_price.loc[row, 'Week']. \
                                     replace('/', '-'), '%Y-%m-%d') #'%Y-%m-%d %H:%M:%S'

try:
    data = addblankcol(data, 12, ['Transaction Year', 'Transaction Month', 'Season'])
    data = addblankcol(data, 16, ['Route Highway Density', 'Doner Highway Density', 'Doner State Area', 'Receiver Highway Density', 'Receiver State Area'])
    data = addblankcol(data, 21, ['Diesel Price'])
except:
    print('Derived Variables already set')
    
for row in range(len(data)):
    #Set time Variable
    #Change date type from string to datetime
    Requested_Pickup_Date = dt.datetime.strptime(data.loc[row, 'Requested Pickup Date']. \
                                             replace('/', '-'), '%Y-%m-%d')
    
    data.loc[row, 'Transaction Year'] = Requested_Pickup_Date.year
    
    data.loc[row, 'Transaction Month'] = Requested_Pickup_Date.month
    data.loc[row, 'Season'] = monthtoseason(data.loc[row, 'Transaction Month'])
    
    #Combine Route Highway Density to data according to Donation State & Receiver State
    Doner_State_Density = Route_Density_Dict[data.loc[row, 'Doner State']][1]
    Doner_State_Area = Route_Density_Dict[data.loc[row, 'Doner State']][2]
    Receiver_State_Density = Route_Density_Dict[data.loc[row, 'Receiver State']][1]
    Receiver_State_Area = Route_Density_Dict[data.loc[row, 'Receiver State']][2]
    Weighted_Route_Density = Doner_State_Density * Doner_State_Area / (Doner_State_Area + Receiver_State_Area) + \
                             Receiver_State_Density * Receiver_State_Area / (Doner_State_Area + Receiver_State_Area)
    
    data.loc[row, 'Route Highway Density'] = Weighted_Route_Density
    data.loc[row, 'Doner Highway Density'] = Doner_State_Density
    data.loc[row, 'Doner State Area'] = Doner_State_Area
    data.loc[row, 'Receiver Highway Density'] = Receiver_State_Density
    data.loc[row, 'Receiver State Area'] = Receiver_State_Area
    
    #Combine Diesel_price to data according to Requested Pickup Date
    data.loc[row, 'Diesel Price'] = findDieselprice(Requested_Pickup_Date, Diesel_price)


#Output of Data Before EDA
data.to_csv('C:/Personal/Wustl-MSCA/Spring 2021/Data Analysist Competition/Competition data/Order_detail_summary---Cleaned Report3.csv')

#-------------------------------------------------------------------------------------------------------------
###Exploratory Data Analysis， EDA
#check the type of Feature & type of data, check if there is null.
data.info(verbose = True) 

#check the mean/sd/maxmin/quantile
data_describe = data.describe()


###Single Feature Analysis
##Abnormalization Analysis
Continuous_Feature = ['Actual Freight Cost', 'Miles', 'Route Highway Density', 'Diesel Price', 'Total Gross Weight', \
                       'FRUITS Gross Weight', 'FRUITS Pack', 'FRUITS Size', 'FRUITS Item Gross Weight', 'FRUITS Quantity', \
                       'VEGETABLES Gross Weight', 'VEGETABLES Size', 'VEGETABLES Item Gross Weight', 'VEGETABLES Quantity']
Discrete_Feature = ['Transaction Year', 'Season', \
                    'Doner State', \
                    'Receiver State', \
                    'Shipping Method Code', \
                    'FRUITS Units', 'VEGETABLES Units']
    
#Continuous Value Abnormalization Analysis
Continuous_Feature_Abnorm_Analysis(Continuous_Feature, 1.5)

#Discrete Value Abnormalization Analysis
Discrete_Feature_Abnorm_Analysis(Discrete_Feature)
    
#Distribution Analysis
Distribution(Continuous_Feature)
Hist(Discrete_Feature)

###Feature Transform
##Set dummy
#---------------------------------------------------------------------------------------------------------------------------------
#Shippment Method Dummy(1 = FA, 0 = Not FA)
for i in range(len(data)):
    if data['Shipping Method Code'][i][:2] == 'FA':
        data.loc[i, 'Shipping Method Code'] = 1
    else:
        data.loc[i, 'Shipping Method Code'] = 0
#Season(Transfer in to Summer{0,1}, Autumn{0,1}, Winter{0,1})
data = addblankcol(data, 15, ['Spring', 'Summer', 'Autumn', 'Winter'])
data[['Spring', 'Summer', 'Autumn', 'Winter']] = 0
for i in range(len(data)):
    if data.loc[i, 'Season'] == 'Summer':
        data.loc[i, 'Summer'] = 1
    elif data.loc[i, 'Season'] == 'Autumn':
        data.loc[i, 'Autumn'] = 1
    elif data.loc[i, 'Season'] == 'Winter':
        data.loc[i, 'Winter'] = 1
    else:
        data.loc[i, 'Spring'] = 1
#Split Year
data = addblankcol(data, 13, ['Year 2018', 'Year 2019', 'Year 2020', 'Year 2021'])
data[['Year 2018', 'Year 2019', 'Year 2020', 'Year 2021']] = 0
for i in range(len(data)):
    if data.loc[i, 'Transaction Year'] == 2018:
        data.loc[i, 'Year 2018'] = 1
    elif data.loc[i, 'Transaction Year'] == 2019:
        data.loc[i, 'Year 2019'] = 1
    elif data.loc[i, 'Transaction Year'] == 2020:
        data.loc[i, 'Year 2020'] = 1
    elif data.loc[i, 'Transaction Year'] == 2021:
        data.loc[i, 'Year 2021'] = 1
#Change Fruit Weight to Discrete
fruit_type_list = ['APPLE', 'APRICOT','BANANA', 'CANTALOUPE', 'CHERRY', 'CITRUS', \
                  'GRAPE', 'GRAPEFRUIT', 'HONEYDEW', 'KIWI', 'LEMON', 'LIME', 'MANDARIN', 'MANGO', \
                  'MELON', 'ORANGE', 'PEACH', 'PEAR', 'PERSIMMON', 'PINEAPPLE', 'PLANTAIN', \
                  'PLUM', 'PRODUCE, BOXES', 'STONE FRUIT, MIXED', 'STRAWBERRY', 'TANGERINE', 'WATERMELON', \
                  'ASPARAGUS', 'BEAN', 'BEET', 'BOK CHOY', 'BROCCOLI', \
                  'BRUSSEL SPROUT', 'CABBAGE', 'CARROT', 'CAULIFLOWER', 'CELERY', 'CHARD', 'CORN', \
                  'CUCUMBER', 'EGGPLANT', 'GREENS', 'GREENS, COLLARD', 'GREENS, MUSTARD', \
                  'KALE', 'LETTUCE', 'ONION', 'PARSNIP', 'PEPPER', 'POTATO', \
                  'PRODUCE, ASSORTED VEGETABLE', 'PUMPKIN', 'RADISH', 'RUTABAGA', \
                  'SQUASH', 'SQUASH, HARD/WINTER', 'SQUASH, SOFT/SUMMER', 'SWEET POTATO', \
                  'TOMATILLO', 'TOMATO', 'TURNIP', 'VEGETABLE']
    
for fruit in fruit_type_list:
    for i in range(len(data)):
        if data.loc[i, fruit] != 0:
            data.loc[i, fruit] = 1
            
#Change Carry Unit into Discrete
carry_units = ['Case', 'Carton', 'Bag', 'Totes', 'Box', 'Crate', 'Bulk box', \
               'Bin', 'Pallet', 'LB']
data = addblankcol(data, 31, carry_units)
data[carry_units] = 0

for i in range(len(data)):
    if len(data.loc[i, 'FRUITS Units']) > 1:
        carry_unit = data.loc[i, 'FRUITS Units']
    else:
        carry_unit = data.loc[i, 'VEGETABLES Units']
    data.loc[i, carry_unit] = 1
    

#---------------------------------------------------------------------------------------------------------------------------------
#Transfer the type object to type int/float
data['Shipping Method Code'] = data['Shipping Method Code'].astype(int)
data['Route Highway Density'] = data['Route Highway Density'].astype(float)
data['Diesel Price'] = data['Diesel Price'].astype(float)
data.info(verbose = True)

data.to_csv('C:/Personal/Wustl-MSCA/Spring 2021/Data Analysist Competition/Competition data/data.csv')
#---------------------------------------------------------------------------------------------------------------------------------


