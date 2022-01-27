# -*- coding: utf-8 -*-
"""
@author: Gorden Li
"""

import pandas as pd

def readasdf(route):
    csv_file = route
    csv_data = pd.read_csv(csv_file, low_memory = False)
    df = pd.DataFrame(csv_data)
    df = df.loc[ : , ~df.columns.str.contains("^Unnamed")]
    return(df)

def clean_0_row(df, col_list):
    for colname in col_list:
        df = df.drop(index = (df.loc[df[colname] == 0].index))
    return df
    
def clean_row(df, col_list_0, col_list_nan):
    df = clean_0_row(df, col_list_0)
    df = df.dropna(subset = col_list_nan)
    return df

def clean_specific_row(df, colname, specific_item_list):
    for item in specific_item_list:
        df = df.drop(index = (df.loc[(df[colname] == item)].index))
    return df

def aggregate_unique(df_from, df_to, colnames_from_list, colnames_to_list, \
                     row, standard):
    assert len(colnames_from_list) == len(colnames_to_list), 'Input length of 2 lists are different'
    ID_Index = list(Order_detail.loc[Order_detail['Document Number'] == standard].index)
    print(ID_Index)
    
    for i in range(len(colnames_from_list)): 
        df_to.loc[row, colnames_to_list[i]] = df_from.loc[ID_Index[0]][colnames_from_list[i]]
    
    #Set nan to 0, otherwise can not do df_to.loc[row, 'Total Gross Weight'] += xxx
    df_to.loc[row, 'Total Gross Weight'] = 0
    df_to.loc[row, 'FRUITS Gross Weight'] = 0
    df_to.loc[row, 'VEGETABLES Gross Weight'] = 0
    
    for ID in ID_Index:
        fruit_num = 0
        vege_num = 0
        display_name = df_from.loc[ID]['Display Name']
        df_to.loc[row, display_name] = df_from.loc[ID]['Total Gross Weight']
        
        if display_name in FRUIT:
            fruit_num += 1
            assert fruit_num == 1, 'More than 1 in fruit' #Check if there is just one type of fruit within---this is the result of data cleaning
            fruit_item_weight = df_from.loc[ID]['Total Gross Weight']
            df_to.loc[row, 'FRUITS Gross Weight'] += fruit_item_weight
            
            df_to.loc[row, 'FRUITS Pack'] = df_from.loc[ID]['Pack']
            df_to.loc[row, 'FRUITS Size'] = df_from.loc[ID]['Size']
            df_to.loc[row, 'FRUITS Units'] = df_from.loc[ID]['Units']
            df_to.loc[row, 'FRUITS Item Gross Weight'] = df_from.loc[ID]['Item Gross Weight']
            df_to.loc[row, 'FRUITS Quantity'] = df_from.loc[ID]['Quantity']
        else:
            vege_num += 1
            assert vege_num == 1, 'More than 1 in vegetable' #Check if there is just one type of vege within---this is the result of data cleaning
            vegetable_item_weight = df_from.loc[ID]['Total Gross Weight']
            df_to.loc[row, 'VEGETABLES Gross Weight'] += vegetable_item_weight
            
            df_to.loc[row, display_name] = df_from.loc[ID]['Total Gross Weight']
            df_to.loc[row, 'VEGETABLES Pack'] = df_from.loc[ID]['Pack']
            df_to.loc[row, 'VEGETABLES Size'] = df_from.loc[ID]['Size']
            df_to.loc[row, 'VEGETABLES Units'] = df_from.loc[ID]['Units']
            df_to.loc[row, 'VEGETABLES Item Gross Weight'] = df_from.loc[ID]['Item Gross Weight']
            df_to.loc[row, 'VEGETABLES Quantity'] = df_from.loc[ID]['Quantity']
            
    df_to.loc[row, 'Total Gross Weight'] = df_to.loc[row, 'FRUITS Gross Weight'] + df_to.loc[row, 'VEGETABLES Gross Weight']
    return df_to

if __name__ == '__main__':
    '''Import Data'''
    Order = readasdf('C:/Personal/Wustl-MSCA/Spring 2021/Data Analysist Competition/Competition data/ProduceFreightSubsidySalesOrdersstart11120 Report 2.csv')
    Order_detail = readasdf('C:/Personal/Wustl-MSCA/Spring 2021/Data Analysist Competition/Competition data/ProduceTransactionReport3ByLineItems Report 3.csv')
    Clean_out = readasdf('C:/Personal/Wustl-MSCA/Spring 2021/Data Analysist Competition/Competition data/Clean out list.csv')
    
    '''Data Cleaning'''
    ###To make sure one ticket, one unit/pack/size in each FA Item Sub Category
    #Deleting 0-value sample in key col among all samples
    Order_detail.info()
    Order_detail = clean_row(Order_detail, ['Total Gross Weight', 'Actual Freight Cost'], ['FA Item Sub Category'])
    #Delete FA Item Sub Category == 'Others'
    #Delete tickets which has multiple units in one single ticket (to make regression easy and it will not cut the info since the num of route didn't decrease)
    #Delete tickets which has data lack in pack, size
    Order_detail = clean_specific_row(Order_detail, 'FA Item Sub Category', ['OTHER'])
    Order_detail = clean_specific_row(Order_detail, 'Document Number', list(set(Clean_out['Document to clean'])))
    
    ###Summarizing all rows of 1 Order(1 unique id) into 1 row by creating nuw dataframe
    #Creat the summary dataframe
    Order_detail_summary = pd.DataFrame(columns = ['Document Number', 'Requested Pickup Date', \
                                                   'Doner', 'Doner Address', 'Doner City', 'Doner State', \
                                                   'Receiver', 'Receiver Address', 'Receiver City', 'Receiver State', \
                                                   'Actual Freight Cost', 'Shipping Method Code', 'Miles', 'Total Gross Weight', \
                                                   'FRUITS Gross Weight', \
                                                   'FRUITS Pack', 'FRUITS Size', 'FRUITS Units', \
                                                   'FRUITS Item Gross Weight', 'FRUITS Quantity', \
                                                   'APPLE', 'APRICOT','BANANA', 'CANTALOUPE', 'CHERRY', 'CITRUS', \
                                                   'GRAPE', 'GRAPEFRUIT', 'HONEYDEW', 'KIWI', 'LEMON', 'LIME', 'MANDARIN', 'MANGO', \
                                                   'MELON', 'ORANGE', 'PEACH', 'PEAR', 'PERSIMMON', 'PINEAPPLE', 'PLANTAIN', \
                                                   'PLUM', 'PRODUCE, BOXES', 'STONE FRUIT, MIXED', 'STRAWBERRY', 'TANGERINE', 'WATERMELON', \
                                                   'VEGETABLES Gross Weight', \
                                                   'VEGETABLES Pack', 'VEGETABLES Size', 'VEGETABLES Units', \
                                                   'VEGETABLES Item Gross Weight', 'VEGETABLES Quantity', \
                                                   'ASPARAGUS', 'BEAN', 'BEET', 'BOK CHOY', 'BROCCOLI', \
                                                   'BRUSSEL SPROUT', 'CABBAGE', 'CARROT', 'CAULIFLOWER', 'CELERY', 'CHARD', 'CORN', \
                                                   'CUCUMBER', 'EGGPLANT', 'GREENS', 'GREENS, COLLARD', 'GREENS, MUSTARD', \
                                                   'KALE', 'LETTUCE', 'ONION', 'PARSNIP', 'PEPPER', 'POTATO', \
                                                   'PRODUCE, ASSORTED VEGETABLE', 'PUMPKIN', 'RADISH', 'RUTABAGA', \
                                                   'SQUASH', 'SQUASH, HARD/WINTER', 'SQUASH, SOFT/SUMMER', 'SWEET POTATO', \
                                                   'TOMATILLO', 'TOMATO', 'TURNIP', 'VEGETABLE'])
    
    #Aggregate data of Order_detail into Order_detail_summary
    list(Order_detail_summary) #Check the colname in Order_detail_summary
    #Set the Document Number
    Order_detail_summary['Document Number'] = list(set(Order_detail.loc[:, 'Document Number']))
    #Aggregate process, starting with dim FRUIT Basket
    FRUIT = ['APPLE', 'APRICOT','BANANA', 'CANTALOUPE', 'CHERRY', 'CITRUS', \
             'GRAPE', 'GRAPEFRUIT', 'HONEYDEW', 'KIWI', 'LEMON', 'LIME', 'MANDARIN', 'MANGO', \
             'MELON', 'ORANGE', 'PEACH', 'PEAR', 'PERSIMMON', 'PINEAPPLE', 'PLANTAIN', \
             'PLUM', 'PRODUCE, BOXES', 'STONE FRUIT, MIXED', 'STRAWBERRY', 'TANGERINE', 'WATERMELON']
 
    for row in range(Order_detail_summary.shape[0]):
        standard = Order_detail_summary.loc[row, 'Document Number']
        print(standard)
        Order_detail_summary = aggregate_unique(Order_detail, Order_detail_summary, \
                                                ['Donation Date', 'Requested Pickup Date', \
                                                   'Donor 1', 'Warehouse 1 Address Line 1', 'Warehouse 1 City', 'Warehouse 1 State', \
                                                   'Name-Receiver/Destination', 'Drop Off Warehouse 1 Address Line 1', 'Drop Off Warehouse 1 City', 'Drop Off Warehouse 1 State', \
                                                   'Shipping Method Code', 'Actual Freight Cost', 'Miles'], \
                                                ['Donation Date', 'Requested Pickup Date', \
                                                   'Doner', 'Doner Address', 'Doner City', 'Doner State', \
                                                   'Receiver', 'Receiver Address', 'Receiver City', 'Receiver State', \
                                                   'Shipping Method Code', 'Actual Freight Cost', 'Miles'], \
                                                row, standard)
    
    Order_detail_summary = Order_detail_summary.fillna(0) #Set nan to be 0
    
    #Output Data
    Order_detail_summary.to_csv('C:/Personal/Wustl-MSCA/Spring 2021/Data Analysist Competition/Competition data/Order_detail_summary---Cleaned Report3.csv')
            
