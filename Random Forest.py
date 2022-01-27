# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 22:23:57 2021

@author: Gorden Li
"""
import pandas as pd
import numpy as np

def readasdf(route):
    csv_file = route
    csv_data = pd.read_csv(csv_file, low_memory = False)
    df = pd.DataFrame(csv_data)
    df = df.loc[ : , ~df.columns.str.contains("^Unnamed")]
    return(df)

def split_train_test(data, test_ratio):
    
    np.random.seed(1)
    
    shuffled_indices = np.random.permutation(len(data)) #generate a list of random with no replacement
    
    test_set_size = int(round(len(data) * test_ratio, 0))
    test_indices = shuffled_indices[:test_set_size]
    train_indices = shuffled_indices[test_set_size:]
    
    return data.iloc[train_indices], data.iloc[test_indices]   


##Import data
data = readasdf('C:/Personal/Wustl-MSCA/Spring 2021/Data Analysist Competition/Competition data/data.csv')

##Random Forest(Random Forest will Feature Filter automatically while doing regression)---Random Forest do not accept one-hot variable, Random Forest do not need to normalization
from sklearn.ensemble import RandomForestRegressor
try:
    data_prepared = data.drop(['Document Number', 'Requested Pickup Date', 'Donation Date', \
                               'Transaction Year', 'Transaction Month', 'Season', \
                               'Doner', 'Doner City', 'Doner Address', 'Doner State', \
                               'Receiver', 'Receiver Address', 'Receiver City', 'Receiver State', \
                               'FRUITS Units', 'VEGETABLES Units', \
                               'Case', 'Carton', 'Bag', 'Totes', \
                               'Box', 'Crate', 'Bulk box', 'Bin', 'Pallet', 'LB'], \
              axis = 1, inplace = False) #Inplace = True mean do the drop to original df; axis = 1 means do to cols
except:
    print('already delete unnecessary row')
#Set train set & test set
data_train, data_test = split_train_test(data_prepared, 0.2)

data_train.info()
features_corr = data_train.corr()['Actual Freight Cost'].abs().sort_values(ascending=False)
features = ['Miles', 'FRUITS Gross Weight', 'PEAR', 'FRUITS Size', 'Route Highway Density', \
                    'VEGETABLES Gross Weight', 'FRUITS Item Gross Weight', 'FRUITS Quantity', 'APPLE', 'STONE FRUIT, MIXED', \
                    'VEGETABLES Quantity', 'VEGETABLES Item Gross Weight', \
                    'Year 2018', 'Year 2019', 'Year 2020', 'Year 2021', \
                    'Spring', 'Summer', 'Autumn', 'Winter']

#Random Forest Fitting
X_train = data_train.drop(['Actual Freight Cost'], axis = 1)
Y_train = data_train['Actual Freight Cost']
X_test = data_test.drop(['Actual Freight Cost'], axis = 1)
Y_test= data_test['Actual Freight Cost']
feat_labels = X_train.columns

rf = RandomForestRegressor(n_estimators=100, max_depth = None, oob_score = True, random_state = 42) 

#rf_pipe = Pipeline([('imputer', SimpleImputer(strategy = 'median')), ('standardize', StandardScaler()), ('rf', rf)])
forest = rf.fit(X_train, Y_train)
Y_Predict = forest.predict(X_test)
result = forest.score(X_test,Y_test) 
print(forest.oob_score_)
##Check the model performance------------------------------------------------------------------------------
#Fearure Importance
importance = forest.feature_importances_

imp_result = np.argsort(importance)[::-1][:15] 

for i in range(len(imp_result)):
    print("%2d. %-*s %f" % (i + 1, 30, feat_labels[imp_result[i]], importance[imp_result[i]]))


feat_labels_important = [feat_labels[i] for i in imp_result]

#Plotting the result of tree
import matplotlib.pyplot as plt
plt.title('Feature Importance')
plt.bar(range(len(imp_result)), importance[imp_result], color='lightblue', align='center')
plt.xticks(range(len(imp_result)), feat_labels_important, rotation=90)
plt.xlim([-1, len(imp_result)])
plt.tight_layout()
plt.show()

# Calculate the absolute errors
errors = abs(Y_Predict - Y_test)
print('Mean Absolute Error:', round(np.mean(errors), 2), 'In Cost.') # Print out the mean absolute error (mae)

# Calculate mean absolute percentage error (MAPE)
x = errors / Y_test
mape = 100 * (errors / Y_test)
# Calculate and display accuracy
accuracy = 100 - np.mean(mape)
print('Mape Error', round(np.mean(mape), 2), '%')
print('Accuracy:', round(accuracy, 2), '%.')

#Hyperparameter Adjustment
max_depths = [i for i in range(5, 21)]
n_estimators = [i for i in range(10, 61)]
OOB_scores = []
for i in range(len(n_estimators)):
    n_estimator = n_estimators[i]
    OOB_scores_of_the_n_estimator = []
    for j in range(len(max_depths)):
        max_depth = max_depths[j]
        rf_adj = RandomForestRegressor(n_estimators = n_estimator, max_depth = max_depth, oob_score = True, random_state = 42)
        forest_adj = rf_adj.fit(X_train, Y_train)
        OOB_scores_of_the_n_estimator.append(forest_adj.oob_score_)
    OOB_scores.append(OOB_scores_of_the_n_estimator)

Heatmap_data = pd.DataFrame(OOB_scores)
Heatmap_data.to_csv('C:/Personal/Wustl-MSCA/Spring 2021/Data Analysist Competition/Analysis/Code/Hyperparameter.csv')
#Heatmap of Hyperparameter Adjustment
import matplotlib.pyplot as plt
import seaborn as sns

#Read Data & Create heatmap
file1= 'C:\Personal\Wustl-MSCA\Spring 2021\Data Analysist Competition\Analysis\Code\Hyperparameter_Heatmap.csv'

pt1=pd.read_csv(file1,index_col=u'OOB_Score')

#Picture1
f, ax1 = plt.subplots(figsize = (8,3))

cmap = sns.cubehelix_palette(start = 1.5, rot = 3, gamma=0.8, as_cmap = True)

p1 = sns.heatmap(pt1, ax=ax1, cmap='rainbow', vmax=0.91, vmin=0.7,linewidths=0.05)
ax1.set_title('Performance[0~1]',fontsize=12)
ax1.set_xlabel('n_estimators')
ax1.set_ylabel('max_depth')

