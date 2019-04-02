# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 14:14:32 2019

@author: MaughanJ1
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 13:58:01 2019

@author: MaughanJ1
"""

import requests
import pandas as pd
import os

# request all team infomation
teams = requests.get('https://fantasy.premierleague.com/drf/teams').json()

# set the empty list for all team data
list_of_team_info = []

for n in range(len(teams)):
    # fitler by each team
    team_info_dict = teams[n]

    # transform into a pd
    pd_team = pd.DataFrame.from_dict(team_info_dict, orient='index').T

    # add to the pre-defined list
    list_of_team_info.append(pd_team)

# concat all the mini-dataframes together
full_team_info = pd.concat(list_of_team_info)[
    ['id', 'name', 'code', 'strength']]


# Functions
def import_team_names():

    r = requests.get('https://fantasy.premierleague.com/drf/teams').json()

    team_id_to_code = {}
    team_name_to_code = {}
    team_code_to_name = {}

    for team_number in range(len(r)):
        team_id_to_code[team_number+1] = r[team_number]['code']
        team_name_to_code[r[team_number]['name']]=r[team_number]['code']
        team_code_to_name[r[team_number]['code']]=r[team_number]['name']

    return [team_id_to_code, team_name_to_code, team_code_to_name]


def import_player_ids():

    # pull the web page in
    r = requests.get('https://fantasy.premierleague.com/drf/elements/').json()

    # export keys and all the values for each player
    headings = list(r[0].keys())
    data_values = [list(r[i].values()) for i in range(len(r))]

    [team_id_to_code, team_name_to_code,
     team_code_to_name] = import_team_names()

    headings.insert(59, 'team name')

    for player_id, player in enumerate(data_values):
        data_values[player_id].insert(59, team_code_to_name[player[3]])

    return data_values


def import_player_headings():
    # pull the web page in
    r = requests.get('https://fantasy.premierleague.com/drf/elements/').json()

    # export keys and all the values for each player
    headings = list(r[0].keys())

    return headings


## Main Funcyions

# core player values.
# gets the unique list of player id and
# player id and player name combinations
# need to join to the master data


list_of_player_core_info = import_player_ids()


player_id_names_list = []
unique_player_ids = []
player_df_list = []

headings = import_player_headings()
headings.append('team_name')

for player in list_of_player_core_info:
    # define the player dataframe
    player_df = pd.DataFrame(player).T
    player_df.columns = headings

    # define the list of player_dfs to concat together later.
    player_df_list.append(player_df)

    # define a unique list of player id - for master file
    unique_player_ids.append(player[0])

player_id_names = pd.concat(player_df_list)  # Sample DataFrame

unique_player_ids.sort(key=int)

# Weekly player data


master = pd.DataFrame()
full_player_scores = []

for player_id in unique_player_ids:
    try:
        # set the number of players in the list
        number_players = max(unique_player_ids)

        # print out the current status of the process
        if player_id % 50 == 0:
            print('Processing player {} of {}...'.format(player_id + 1,
                                                         number_players))

        # request performance data for one player
        r = requests.get(
            'https://fantasy.premierleague.com/drf/element-summary/' + str(
                player_id)).json()

        # check the historic data
        hist = r['history']

        # create a list of player dataframe
        player_scores = []

        # loop through to get individual gameweeks
        for gw, scores in enumerate(hist):
            # change the GW to string for columns purposes
            GW = str(gw)

            # change the json into pandas format
            pd_scores = pd.DataFrame.from_dict(scores, orient='index').T

            # set the gameweek values - dont already have a round column
            # pd_scores['gameweek'] = GW

            # set the player_id
            pd_scores['player_id'] = player_id

            # concat to the master
            player_scores.append(pd_scores)

        # join all the player scores together
        player_scores1 = pd.concat(player_scores)

        # join each of the players to the list
        full_player_scores.append(player_scores1)
    except:
        print('{} : Did not pass'.format(player_id))


breaker = 'break'

# join together
master_points_file = pd.concat(full_player_scores)

# change the names of the columns to represnet its either oppeonent team of the one he plays for
full_team_info_cols = full_team_info.columns
player_team = full_team_info
opp_team = full_team_info

# do for the current team
player_cols_all=[]

# loop through and change column names
for i in full_team_info_cols:
    col = 'team_' + i
    player_cols_all.append(col)

# chagne the columns to be more specific
player_team.columns = player_cols_all

# repeat again for the opponent aswell.
opp_cols_all=[]

# loop through and change column names
for j in full_team_info_cols:
    col = 'opp_' + j
    opp_cols_all.append(col)

# chagne the columns to be more specific
opp_team.columns = opp_cols_all

# join the opp_info and team_info to the master_points list.
master_file_join_1 = pd.merge(master_points_file, opp_team,
                              left_on ='opponent_team', right_on='opp_id',
                              how='left')

# Download the team data

# request all team infomation
teams = requests.get('https://fantasy.premierleague.com/drf/teams').json()

# set the empty list for all team data
list_of_team_info = []

for n in range(len(teams)):
    #fitler by each team
    team_info_dict = teams[n]
    
    # transform into a pd
    pd_team =  pd.DataFrame.from_dict(team_info_dict, orient='index').T
    
    # add to the pre-defined list
    list_of_team_info.append(pd_team)

# concat all the mini-dataframes together
full_team_info = pd.concat(list_of_team_info)
teams_id = full_team_info[['name','id']]
 
# function to clean up next game fixture 

def clean_next_fixture_opp(row):
    try:
        next_game = row['next_event_fixture'][0]
        for k,v in next_game.items():
            if k == 'opponent':
                against = v
        
        new_team = teams_id.loc[teams_id.id == against, teams_id.columns]
        new_team_name = new_team.name
    except:
        new_team_name = ''
    return new_team_name 

def clean_next_fixture_home(row):
    try:
        next_game = row['next_event_fixture'][0]
        for k,v in next_game.items():
            if k == 'is_home': 
                is_home = v
    except:
        is_home=''
    return is_home 


full_team_info['against'] = full_team_info.apply(lambda row: clean_next_fixture_opp(row), axis=1)
full_team_info['is_home'] = full_team_info.apply(lambda row: clean_next_fixture_home(row), axis=1)

# jsut get codes and ids for teams
# save the files to a csv
data_path  = 'C:/Users/maughanj1/Documents/ukds/Play/FPLgorithm/'

master_file_join_1.to_csv(data_path + 'gameweek_scores.csv')
player_id_names.to_csv(data_path + 'player_data.csv')
full_team_info.to_csv(data_path + 'team_data.csv')
