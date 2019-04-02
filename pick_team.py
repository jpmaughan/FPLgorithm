# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 10:21:35 2019

@author: MaughanJ1
"""

# Use the predictions for the next gameweekt to create a team
import pandas as pd

# initilise for hte next gameweeks.
next_gw = 31

# save the files to a csv
data_path  = 'C:/Users/maughanj1/Documents/ukds/Play/FPLgorithm/'

# player data
pdf = pd.read_csv(data_path + 'player_data.csv')
predict_set_next = pd.read_csv(data_path + 'next_week_preds.csv')

# predicted set
predict_set_prev = pd.read_csv(data_path + 'predictions_rf.csv').drop(columns=['points_binary'])

# concatenate btoh training weeks and next weeks rounds.
predict_set = pd.concat([predict_set_prev, predict_set_next])


# double gameweek teams
dgw_teams = ['West Ham', 'Chelsea', 'Liverpool', 'Everton', 'Huddersfield',
       'Leicester', 'Newcastle', 'Fulham', 'Burnley', 'Bournemouth']

def double_gameweek(row):
    
    team = row['team_name']
    pred = row['pred']
    if team in dgw_teams:
        pred = row['pred'] * 2
        
    return pred
    
# current gameweek
# add a filter whihc i chance of plyaoing this round.
# try predict using (in_dream_team) or not.
# do some kind of optimisation techniques.
# add a filter to remove options of the people that dont hav e game this week


# initialise the toatal_points at he tart of the season to be 0
total_points= 0
gk_points = 0
df_points = 0
mf_points = 0
fw_points = 0

# initialise the empty list
all_teams = []
all_squads = []
print('Skip GW1')

for gw in range(1, next_gw+1):

    # current gameweek 
    this_gw = predict_set.loc[predict_set.gameweek == gw, predict_set.columns]
    
    if gw == 1:
        pass
    else:
        this_gw = this_gw.loc[this_gw.f_minutes > 20, this_gw.columns]    
    

    # get the most
    highest = this_gw.sort_values(['pred'], ascending=False)[['pred', 'name', 'points', 'player_id']]
    
    # join to their position
    highest_score = 1
    
    # get rhe predicted score
    highest['pred_score'] = highest.apply(lambda row: row['pred']*highest_score, axis=1)
    
    # join the datasets
    join_df = pd.merge(highest, pdf, left_on='player_id', right_on='id', how='inner')
    
    # double gw teams
    join_df['pred_score'] = join_df.apply(lambda row: double_gameweek(row), axis=1)
    
    print(join_df.team_name.unique())
    # create the team
    class DreamTeam:
        
        def __init__(self, join_df=join_df):
            self.df = join_df       
    
        def top_position(self, position):
            #1=gk,  2 -def , 3 = mid , 4 =fwd
            df = self.df
            
            # hard-code some limitations into it for now
            df = df.fillna(100)
            playing2 = df.loc[df.chance_of_playing_next_round >= 50, df.columns]
            playing3 = playing2.loc[playing2.chance_of_playing_this_round >= 50, playing2.columns]
            #playing4 = playing3.loc[playing3.chance_of_playing_this_round == 100, playing3.columns]
            playing = playing3.loc[playing3.points_per_game >= 3, playing3.columns]

            keepers = playing.loc[playing.element_type == position, playing.columns]
            
            top_keepers = keepers.sort_values(['pred_score'], ascending=False).head(5)
            return top_keepers
        
        def create_team(self):
            # needs some stronger coding for optimaisting the value side of the team.
            # this need to be sorted - getting two keepers in the output/
            # core team
            tk = self.top_position(position=1).head(2)
            td = self.top_position(position=2).head(5)
            tm = self.top_position(position=3).head(5)
            tf = self.top_position(position=4).head(3)
            
            # shuffle formation - proper 
            sk = tk.tail(1)
            sd = td.tail(2)
            sm = tm.tail(3)
            sf = tf.tail(2)
            
            
            # extra players
            extra_team1 = pd.concat([sd,sm,sf]).sort_values(['pred'], ascending=False)
            extra_team = extra_team1.head(4)
            subs = pd.concat([sk, extra_team1.tail(3)])#[['points','web_name','pred','element_type','now_cost']]
            
            # create the final team
            all_team = pd.concat([tk.head(1),td.head(3),tm.head(2),tf.head(1), extra_team])#[['points','web_name','pred','element_type','now_cost']]
            
            # this forces the formation 3-5-2
            # all_team = pd.concat([tk.head(1),td.head(3),tm.head(5),tf.head(2)])#[['points','web_name','pred','element_type','now_cost']]

            # add the subs to the end of the list.
            out_team = pd.concat([all_team.sort_values(['element_type'], ascending=True), subs.sort_values(['element_type'], ascending=True)])
            
            # get list of all in 
            cost = out_team['now_cost'].sum()
            
            # gives a base line of the team being too expensive.
            if cost > 1000:
                print('Too expensive - £ {}'.format(cost/10))
                
            return out_team.head(11), out_team
 
    # get the starting 11 we would have - then the subs / squad too.
    starting_x, squad_x = DreamTeam().create_team()
    
    # mid / fwd for captain
    cap_df = starting_x.loc[starting_x.element_type > 2, starting_x.columns]
        
    # get the points for the captain.
    cap_points =  cap_df.sort_values(['pred'], ascending=False).head(1).points.values[0]
    
    # get the captain namec
    cap_name =  cap_df.sort_values(['pred'], ascending=False).head(1).web_name.values[0]
    
    # get the actual points
    team_points = starting_x['points'].sum()
    
    # get the cumulative score over the season    
    total_points += team_points + cap_points

    # append the gw team to a list of all teams.
    all_teams.append(starting_x)
    
    # append the whole squad
    all_squads.append(squad_x)
    
    # get each position set.
    gk = squad_x.loc[squad_x.element_type == 1, squad_x.columns]['points'] 
    df = squad_x.loc[squad_x.element_type == 2, squad_x.columns]['points'] 
    mf = squad_x.loc[squad_x.element_type == 3, squad_x.columns]['points'] 
    fw = squad_x.loc[squad_x.element_type == 4, squad_x.columns]['points'] 
     
    # total points         
    gkp = gk.sum()
    dfp = df.sum()
    mfp = mf.sum()
    fwp = fw.sum()
    
    # add the running points
    gk_points = gk_points + (gkp / 2)
    df_points = df_points + (dfp / 5)
    mf_points = mf_points + (mfp / 5)
    fw_points = fw_points + (fwp / 3)
    
            
    print('Gameweek {} : {}    -  (C) {} : {} Points'.format(gw, team_points, cap_name, cap_points))
    print('   {}-{}-{}   '. format(len(df), len(mf), len(fw)))
    print('              GK {},   DF {},   MF  {},  FW   {}'.format(gkp,dfp,mfp,fwp))
    print('')
    
print('Season: {}'.format(total_points))
print('')
print('Points per player - Postion')
print('')
print(' GK: {}   ,  DF:  {}  ,  MF  {}   ,   FW  {} '.format(gk_points , df_points , mf_points , fw_points ))


# base outcomes for each of the formations
# 3-4-3 is 2794
# 5-3-2 is 2712
# 4-4-2 is 2786
# 3-5-2 is 2822
# 4-5-1 is 2769
# 5-4-1 is 2720
# Note this is way too overfitted.
# Create a function that runs all of the above files. 
# an amalgamtion of the data.
 
# see who the model picks the most

season_player = pd.concat(all_squads)
fwdS = season_player.loc[season_player.element_type == 4, season_player.columns] 
midS = season_player.loc[season_player.element_type == 3, season_player.columns]

defS = season_player.loc[season_player.element_type == 2, season_player.columns]
gkS = season_player.loc[season_player.element_type == 1, season_player.columns]

s_fwd = fwdS.second_name.value_counts()
s_mid = midS.second_name.value_counts()
s_def = defS.second_name.value_counts()
s_gk  = gkS.second_name.value_counts()


## double those that have a duble gameweek

## Save final one to csv

squad_x.to_csv(data_path + 'fantasy_prediction.csv')

# Score to beat - 1208 
# GK: 73.5  
# DF: 58.6  
# MF: 114.4 
# FW: 125.66
