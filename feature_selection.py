# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 14:13:56 2019

@author: MaughanJ1
"""

# Relaod the data
import pandas as pd


# do this in order to get the rank of each player after each gameweek.
# get the cumulative score to that point for each of the field 
# then the package below i think.
import scipy.stats as ss

# save the files to a csv
data_path  = 'C:/Users/maughanj1/Documents/ukds/Play/FPLgorithm/'

# historic data
hdf = pd.read_csv(data_path + 'gameweek_scores.csv')
pdf = pd.read_csv(data_path + 'player_data.csv')
tdf = pd.read_csv(data_path + 'team_data.csv')

# core player data 
cpdf = pdf[['first_name','second_name', 'id','team_name' ,'team']]

# join for a full_dataset
full_df = pd.merge(hdf, cpdf, left_on=['player_id'], right_on=['id'], how='left')

# next gameweek data.
teams = hdf.drop_duplicates(['round','opp_code'])

# get a list of fixtures think i've got the code.
# Get the target variable X
# Get a function that joins to previous weeks of data.
# get form as a function

# get the dates of games into a suitable foramt.

last_gw = max(hdf['round'])  
next_gw = last_gw + 1 

def team_goals(df, for_team=True):
    g=0
    for row in df.iterrows():
        wh = row[1]['was_home']
        hg = row[1]['team_h_score']
        ag = row[1]['team_a_score']
        if wh == for_team:
            g+=hg
        else:
            g+=ag
    
    return(g)

## add a category for season stats might include just having gw=prev_gw
## could be good to have for the whole team really. intersting to see how a 
    ## whole defnec ei performing./


     
class Player:
    """
    Class that defines a player. With Historic / Future Datframe provided above
    """
    # set up the input data 
    # TODO: Alter to gameweek can be changed easily.
    
    def __init__(self, ids, pdf=pdf, hdf=hdf, last_gw=last_gw):
        self.ids = ids # id for the player you want
        self.pdf = pdf.loc[pdf.id == self.ids, pdf.columns] # core player dataframe
        self.hdf = hdf.loc[hdf.player_id == self.ids, hdf.columns] # historic game dataframe
        self.last_gw = last_gw # max(self.hdf['round'])
        self.name = str(self.pdf['first_name'] + ' ' + self.pdf['second_name'])
        self.hdf_all = hdf 
            
    # historical  data  -  FORM     
    
    def form(self, column='total_points', prev_weeks=3):
        ' Change the colum we want to form / how many recent weeks we want'
        df = self.historic_games()
        # define range of the gameweek form
        current_gw = self.last_gw + 1
        lower_gw = current_gw - prev_weeks
        # filter on gameweek form.
        filter_df = df.loc[df.gameweek >= lower_gw, df.columns] 
        filter_df2 = filter_df.loc[filter_df.gameweek < (current_gw), filter_df.columns]        
        total_sum = filter_df2[column].sum()
        form = total_sum / prev_weeks
        return form
       
    # define the player databases    
        
    def player_data(self):
        pdf = self.pdf
        player_df = pdf.loc[pdf.id == self.ids, pdf.columns]
        return player_df
    
    def historic_games(self):
        hdf = self.hdf
        player_df = hdf.loc[hdf.player_id == self.ids, hdf.columns]
        player_df['gameweek'] = player_df.apply(lambda row: int(row['round']), axis=1)
        player_df = player_df.loc[player_df.gameweek <= self.last_gw, player_df.columns ]
        return player_df
    
    
top_players  = []
new_df = pd.DataFrame(columns=['name','score'])

for i in range(1,575):
    score = Player(i, last_gw=6).form( )
    name = Player(i).name
    row = [name, score]
    new_df.loc[len(new_df)] = row
    
# get the full fixture list 

class Team:
    # TODO: 
    def __init__(self, ids, tdf=tdf, full_df=full_df, last_gw=last_gw):
        self.tdf_team = tdf.loc[tdf.id == ids, tdf.columns]
        self.pdf_team = full_df.loc[full_df.team == ids, full_df.columns]
        self.last_gw = last_gw
        
    def goals(self, for_team=True, prev_weeks=3):
        # set the team boundary
        df = self.pdf_team
        # define the current gameweek
        current_gw = self.last_gw + 1
        diff = current_gw - prev_weeks
        # change the gameweek into an integer to be measured against
        df['gameweek'] = df.apply(lambda row: int(row['round']), axis=1)
        #fitler by gamewee
        filter_df = df.loc[df.gameweek >= diff, df.columns]   
        filter_df1 = filter_df.loc[filter_df.gameweek < (current_gw), filter_df.columns]
        filter_df2 = filter_df1.drop_duplicates(['gameweek'])
        # select the column and sum
        goals = team_goals(filter_df2, for_team=for_team)
        return goals
    
    # def form_all_players(self, 'total_points', prev_weeks=3)
       # # set the team boundary
       # df = self.pdf_team
       # # define the current gameweek
       # current_gw = self.last_gw + 1 
       # diff = current_gw - prev_weeks
       # # change the gameweek into an integer to be measured against
       # df['gameweek'] = df.apply(lambda row: int(row['round']), axis=1)
       # #fitler by gameweek
       # filter_df = df.loc[df.gameweek >= diff, df.columns]   
       # filter_df2 = tests.drop_duplicates(['gameweek'])
       # len_df = len(filter_df2)
       # # select the column and sum
       # total_sum = filter_df2[column].sum()
        #form = total_sum / prev_weeks
       # return filter_df
    
    def historic_game_difficulty(self, prev_weeks=3):
        df = self.pdf_team
        # define the current gameweek
        current_gw = self.last_gw + 1
        diff = current_gw - prev_weeks
        # change the gameweek into an integer to be measured against
        df['gameweek'] = df.apply(lambda row: int(row['round']), axis=1)
        # filter hte gameweejs
        filter_df = df.loc[df.gameweek >= diff, df.columns].drop_duplicates('gameweek')    
        filter_df2 = filter_df.loc[filter_df.gameweek < (current_gw - 1), filter_df.columns]
        total_sum = filter_df2['opp_strength'].sum()
        opp_ave_diff = total_sum / prev_weeks
        return opp_ave_diff
    
 
    
# Start creating the test and train set. #

# Filter to save time - only ones with minutes
no_minutes = full_df.loc[full_df.minutes != 0, full_df.columns]

# assign df
df = no_minutes

# Dependent Variable
X = df[['total_points', 'second_name', 'round', 'was_home']]

# Independent Variable
# combinations that need predicted
combinations = df[['round', 'id_y', 'team', 'opp_id', 'total_points', 
                   'opp_strength', 'value', 'was_home', 'selected']]


# need to include the next gameweek in this function
# just need to change this function now ?
# get some client infomatio
# next game diff?

def features_creation(row, gw):
    pid = row['id_y']
    tfid = row['team']
    taid = row['opp_id']
    value = row['value']
    opp_strength = row['opp_strength']
    selected = row['selected']
    
    lgw = gw - 1
    # Get the dependent variable
    target_points = row['total_points']
    home = row['was_home']

    # Get the players individual performance
    player_class = Player(pid, last_gw=lgw) 
    
    # player stats 
    player_name = player_class.name
    
    # season_stats - player - done per minute ? could be done by gameweek 
    # jsut swap the gw for s_minutes and visa versa
    # these will have to be done in form of rank
    # the multiplication by gameweek might need to be changed
    # or to number of minutes played.
    s_minutes =  player_class.historic_games().minutes.sum()
    s_points = player_class.form(prev_weeks=gw) * s_minutes
    s_keypass = player_class.form(column='key_passes', prev_weeks=gw) * s_minutes
    s_threat = player_class.form(column='threat', prev_weeks=gw) * s_minutes 
    s_creativity = player_class.form(column='creativity', prev_weeks=gw) * s_minutes
     
    # form stats - player
    f_points = player_class.form()
    f_bps = player_class.form(column='bps')
    f_tranf_in = player_class.form(column='transfers_in', prev_weeks=1)
    f_tranf_out = player_class.form(column='transfers_out', prev_weeks=1)
    f_threat = player_class.form(column='threat')
    f_minutes = player_class.form(column='minutes', prev_weeks=1)
    f_completed_pass = player_class.form(column='completed_passes', prev_weeks=10)
    
      
    # Team for stats
    team_for = Team(tfid, last_gw=lgw)
    tf_goals = team_for.goals()
    tf_conc  = team_for.goals(for_team=False)
    tf_diff  = team_for.historic_game_difficulty()
    
    # Team against stats
    team_against = Team(taid, last_gw=lgw)
    ta_goals = team_against.goals()
    ta_conc = team_against.goals(for_team=False)
    ta_diff = team_against.historic_game_difficulty()
    
    #print(player_name, gw, ta_diff, tf_diff)
    row2 = [player_name, pid, gw, selected, target_points, f_points, f_bps, tf_goals, tf_conc,
            tf_diff, ta_goals, ta_conc, ta_diff, f_tranf_in, f_tranf_out, f_minutes,
            f_completed_pass, s_points, s_keypass, s_threat, s_creativity, opp_strength,
            value, f_threat, home]
    
    return row2

# think about adding the most recent totw 
# Need to make sure these line up with row2 above
# could be worth making this a function at some pooints and laide with th emodellign.
features_columns = ['name','player_id', 'gameweek', 'selected', 'points', 'points_form',
                    'bps_form', 'tf_goals', 'tf_conc', 'tf_diff',
                    'ta_goals', 'ta_conc', 'ta_diff', 'trans_in', 'trans_out',
                    'f_minutes', 'comp_pass_10', 'season_points', 'season_kp', 'season_threat',
                    'season_creativity', 'opp_strength', 'value', 'f_threat',
                    'home']
 
# initialise the dfy
    
y = pd.DataFrame(columns=features_columns)

length_comb = len(combinations)
proccess_n = 0
    

for index, row in combinations.iterrows():
    proccess_n += 1
    
    # print out the current status of the process
    if proccess_n % 100 == 0:
        print('Processing player {} of {}...'.format(proccess_n + 1,
                                                     length_comb))
    #Gameweek / playerid / team_for id / team against id
    gw = row['round']
        
    # use the featueres reation funciton
    row = features_creation(row, gw=gw)
    
    # append to the dataframe
    y.loc[len(y)] = row
    

y.to_csv(data_path + 'predict_set.csv')
 
# repeat for the next gameweek aswell 
# maybe functionise too 
    
# need to include the next gameweek in this function

combinations_next = df.drop_duplicates(['id_y'])

# Initialise the dataframe
yn = pd.DataFrame(columns=features_columns)

# think that should work - shame if not.
# pd.DataFrame(columns=['name','player_id', 'gameweek', 'points', 'points_form',
#                          'bps_form', 'tf_goals', 'tf_conc', 'tf_diff',
#                          'ta_goals', 'ta_conc', 'ta_diff'])


length_comb = len(combinations_next)
proccess_n = 0


for index, row in combinations_next.iterrows():
    proccess_n += 1
    gw=next_gw
    # print out the current status of the process
    if proccess_n % 50 == 0:
        print('Processing player {} of {}...'.format(proccess_n + 1,
                                                     length_comb))
    #Gameweek / playerid / team_for id / team against id
    gw = next_gw
    
    # use the featueres reation funciton
    row = features_creation(row, gw=gw)
        
    # append to the dataframe
    yn.loc[len(yn)] = row
    

    
yn.to_csv(data_path + 'next_week.csv')