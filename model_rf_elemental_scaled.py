# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 09:45:02 2019

@author: MaughanJ1
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 21:14:59 2019

@author: MaughanJ1
"""

# split into different elements
 
# import packages
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import pickle
from sklearn import preprocessing
from keras.callbacks import ModelCheckpoint
from sklearn import preprocessing
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from keras.layers.normalization import BatchNormalization
from sklearn.preprocessing import MultiLabelBinarizer

# gameweek just gone
gw=31

# scale the

all_predictions = []
all_predictions_next = []

number_of_features = 6

## Set up the model
def change_to_binary(row):
    p = row['points']
    if int(p) > 6:
        out = 1
    else:
        out = 0
        
    return out

# save the files to a csv
data_path  = 'C:/Users/maughanj1/Documents/ukds/Play/FPLgorithm/'

# create a list of features for each 
def season_to_form(row, column_name):
    season_stat = row[column_name]
    gw = row['gameweek']
    divgw = max(1, gw-1)
    seas_per_game = season_stat / divgw
    return seas_per_game

def was_home_encoder(row):
    was_home = row['home']
    if was_home:
        out = 1
    else:
        out = 0
    
    return out

def proportional_transfers(row):
    trin = row['trans_in']
    trout = row['trans_out']
    selec = row['selected']
    diff = trin - trout
    try:
        out = diff / selec
    except:
        out = 0
    return out

def differential(row):
    selected = row['selected']
    if selected > 500000:
        out = 1
    else:
        out = 0
    return out

predict_set1 = pd.read_csv(data_path + 'predict_set.csv')
predict_set1 = predict_set1.dropna(axis=1)


def prepare_dataset(df, position, future=False): 
    # historic data

    pdf = pd.read_csv(data_path + 'player_data.csv')
    
    # change some seasonal stats to season form
    df['season_points'] = df.apply(lambda row: season_to_form(row, 'season_points'), axis=1)
    df['season_kp'] = df.apply(lambda row: season_to_form(row, 'season_kp'), axis=1)
    df['season_threat'] = df.apply(lambda row: season_to_form(row, 'season_threat'), axis=1)
    df['season_creativity'] = df.apply(lambda row: season_to_form(row, 'season_creativity'), axis=1) 
    df['was_home'] = df.apply(lambda row: was_home_encoder(row), axis=1) 
    df['trans_prop'] = df.apply(lambda row: proportional_transfers(row),axis=1)
    df['differential'] = df.apply(lambda row: differential(row),axis=1)
    
    # This is temperary code - should be put in the feature selection.
    player_postion = pdf[['id', 'element_type']]
    
    # join predict_set to the 
    predict_set = pd.merge(df, player_postion, left_on=['player_id'], right_on=['id'], how='inner') 
    
    # filter by position
    predict_set = predict_set.loc[predict_set.element_type == position, predict_set.columns]   
    
    # filter for after the first week
    # predict_set = predict_set.loc[predict_set.gameweek > 1, predict_set.columns]
    
    # change to a binary yes or no
    predict_set['points_binary'] = predict_set.apply(lambda row: change_to_binary(row), axis=1)
    
    
    # 2. Setting target / explanatroy variables.
    
    # one hot encode target variable 
    #y = predict_set.points_binary
    y = predict_set.points 
    
    # order the gaemweesks to not incnldue knoweldge of the future
    predict_set = predict_set.sort_values(['gameweek'], ascending=True)
    
    # scale feature space  
    #X = predict_set.drop(columns = ['points', 'points_binary', 'name',
    #                                'gameweek',  'player_id', 'Unnamed: 0'])
    
    # Don't drop the gameweek just yet
    X = predict_set.drop(columns = ['points', 'points_binary', 'name', 
                                    'player_id', 'Unnamed: 0'])
        
    # select the features we want
    features = ['points_form'
                ,'bps_form'
                ,'differential'
                ,'tf_goals'# block thse out inbetween gameweeks.
                ,'tf_conc'
                ,'tf_diff' # team against / for are the least important features.
                ,'ta_goals'
                ,'ta_conc'
                ,'ta_diff'
                ,'trans_in'
                ,'trans_out'
                ,'trans_prop'
                ,'f_minutes'
                #,'comp_pass_10'
                #,'element_type'
                #,'season_points'
                #,'season_kp'
                #,'season_threat'
                #,'season_creativity'
                ,'opp_strength'
                ,'value'
                ,'f_threat'
                ,'was_home'
                ,'selected'
                 ]
    
    scaled_gw=[]
    
    # needs to change 
    if future:
        gamew = df.gameweek.max()
        X_gw = X.loc[X.gameweek == gamew]
        X_cont = X_gw[features]
        #X_cat = X_gw[cat_var]
        # scale feature space  
        scaler = preprocessing.MinMaxScaler(feature_range=(-1, 1))
        Xs = scaler.fit_transform(X_cont)
        X_out = pd.DataFrame(Xs, columns=features)
    else:
        for gamew in range(df.gameweek.min(), gw+1):
            X_gw = X.loc[X.gameweek == gamew]
            X_cont = X_gw[features]
            #X_cat = X_gw[cat_var]
            # scale feature space  
            scaler = preprocessing.MinMaxScaler(feature_range=(-1, 1))
            Xs = scaler.fit_transform(X_cont)
            #X_out = pd.concat([Xs, X_cat], axis=1)
            Xs = pd.DataFrame(Xs, columns=features )
            scaled_gw.append(Xs)
        X_out = pd.concat(scaled_gw)
    #X = pd.concat(scaled_gw, axis=1)
    
    

    
    # can do some colinearlyity sting here just as dimensioality of the tdata
    
    # filter by the feautes
    X_out = X_out[features]
    
    # drop if the columns are NA
    #X_out = X_out.dropna(axis=1)
    
    #if scale:
    #    # scale feature space  
    #    scaler = preprocessing.MinMaxScaler(feature_range=(-1, 1))
    #    Xs = scaler.fit_transform(X)

    return X_out, y, features, predict_set


test_split = 1 / gw
# a lo
#Xs, y, features, pred_df = prepare_dataset(pred_df1)
#Xs = Xs.dropna(axis=1)
#columns_Xs = Xs.columns



# actual get the old and new set into the same dataframe 
# loop through each game week and scale that way = or over the whole season 

for i in range(1,5):
    
    # 1. Preproccess the historic Data
    
    # historic dataset 
    df_old = pd.read_csv(data_path + 'predict_set.csv').dropna(axis=1)
    
    # Get the suitable dataframe - features - sets
    X, y, features, predict_set = prepare_dataset(df_old, i)
    
    # define the feature lsit
    feature_list = list(X.columns)
   
    # 2. Get the list of the most important features
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_split, random_state = 42, shuffle = False)
     
    # Instantiate model with 200 decision trees
    rf = RandomForestRegressor(n_estimators = 200, random_state = 42)
    # Train the model on training data
    rf.fit(X_train, y_train)
    
    # get the importances
    importances = list(rf.feature_importances_)
    
    # get the top n features
    top_features=pd.DataFrame()
    top_features['imp'] = importances
    top_features['fea'] = features
    topf = top_features.sort_values(['imp']).tail(number_of_features)['fea']
    # 3.2 Model : Train the actual Model  
    
    # filter by the features
    X = X[topf]
    
    # define the feature lsit
    feature_list = list(X.columns)
    
    # train test split 
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_split, random_state = 42, shuffle = False)
    
    # Import the model we are using
    
    # Instantiate model with 1000 decision trees
    rf = RandomForestRegressor(n_estimators = 200, random_state = 42)
    
    # Train the model on training data
    rf.fit(X_train, y_train)
    
    # 4. Train on whole historical dataset.    
    
    # get the predictions of the whole dataset
    predictions = rf.predict(X)
 
    # link these predictions to an actual names.
    predict_set['pred'] = predictions
    
    # save the first set of predictions
    all_predictions.append(predict_set)


    # TODO: Replace only some of the most important features.
    

    # 5. Predict next weeks team - basically the same as step 1.
    
    # prediction set - for next week
    pred_df1 = pd.read_csv(data_path + 'next_week.csv')
    pred_df1 = pred_df1.dropna(axis=1)
    
    # get the appropriate features
    X, y, features, pred_df = prepare_dataset(pred_df1, i, future=True)
    
    # also select the features
    X = X[topf]
       
    # re-run the model on the next weeks data
    predictions = rf.predict(X)
    
    # attach predictions to original
    pred_df['pred'] = predictions
    
    all_predictions_next.append(pred_df)
    
    # 5. Analysis 
    

    # get the importances
    importances = list(rf.feature_importances_)
    
    # Set the style
    plt.style.use('fivethirtyeight')
    
    # list of x locations for plotting
    x_values = list(range(len(importances)))
    
    # Make a bar chart
    plt.bar(x_values, importances, orientation = 'vertical',alpha=0.4)
    
    # Tick labels for x axis
    plt.xticks(x_values, feature_list, rotation='vertical')
    
    # Axis labels and title
    plt.ylabel('Importance'); plt.xlabel('Variable'); plt.title('Variable Importances');
    
    # show the plot
    plt.show()
    
     

all_preds = pd.concat(all_predictions)
all_preds_next = pd.concat(all_predictions_next)
# save next weeks predictions.
    

all_preds.to_csv(data_path + 'predictions_rf.csv')

all_preds_next.to_csv(data_path + 'next_week_preds.csv')
 