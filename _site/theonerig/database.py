# AUTOGENERATED! DO NOT EDIT! File to edit: 05_database.ipynb (unless otherwise specified).

__all__ = ['get_db_engine', 'prompt_credentials', 'get_record_essentials', 'get_stim_params', 'get_table',
           'stim_param_to_dict']

# Cell
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, select

import pandas as pd
import getpass
import json

# Cell
def get_db_engine(username, password, ip_adress, model_name, rdbms="mysql"):
    engine = create_engine("%s://%s:%s@%s/%s" % (rdbms, username, password, ip_adress, model_name),echo = False)
    test_query = "SELECT * FROM Project"
    pd.read_sql_query(test_query, engine)
    return engine

def prompt_credentials(user=None, db_adress=None):
    if user is None:
        user = input(prompt='Username: ')
    passwd = getpass.getpass(prompt='Password: ')
    if db_adress is None:
        db_adress = input(prompt='DB IP: ')
    return user, passwd, db_adress

# Cell
def get_record_essentials(engine, record_id):
    q_select_record = "SELECT * FROM Record WHERE id = %d" % record_id
    q_select_cell = "SELECT * FROM Cell WHERE record_id = %d" % record_id

    df_record = pd.read_sql_query(q_select_record, engine)
    df_cell = pd.read_sql_query(q_select_cell, engine)

    experiment_id = df_record["experiment_id"][0]
    q_select_experiment = "SELECT * FROM Experiment WHERE id = %d" % experiment_id
    df_experiment = pd.read_sql_query(q_select_experiment, engine)

    mouse_id = df_experiment["mouse_id"][0]
    q_select_mouse = "SELECT * FROM Mouse WHERE id = %d" % mouse_id
    df_mouse = pd.read_sql_query(q_select_mouse, engine)

    tool_id = df_record["tool_id"][0]
    q_select_tool = "SELECT * FROM Tool WHERE id = %d" % tool_id
    df_tool = pd.read_sql_query(q_select_tool, engine)

    q_select_map = "SELECT * FROM Map WHERE tool_id = %d" % tool_id
    df_map =  pd.read_sql_query(q_select_map, engine)

    res_dict = {"record": df_record, "cell": df_cell,
                "experiment": df_experiment, "mouse": df_mouse,
                "tool": df_tool, "map": df_map}
    return res_dict

# Cell
def get_stim_params(engine, stim_hashes):
    #Writting the query speed up the function rather than querying all individual tables
    # and filtering them all
    if not isinstance(stim_hashes, list):
        stim_hashes = [stim_hashes]
    if len(stim_hashes)==1:
        str_hashes = "('"+stim_hashes[0]+"')"
    else:
        str_hashes=str(tuple(stim_hashes))
    query = """SELECT Stim.name AS stim_name, description, barcode, stim_comment, stimulus_id,
                screen_id, hash, date AS date_compiled, compiled_comment, compiled_id, parameter_id,
                Parameter.name as param_name, value as param_value
                FROM (SELECT Compiled.id as comp_id, name, description, barcode, Stimulus.comment AS stim_comment, stimulus_id, screen_id, hash, date, Compiled.comment AS compiled_comment FROM Stimulus
                LEFT JOIN Compiled ON stimulus_id=Stimulus.id WHERE hash IN """+str_hashes+""") AS Stim
                LEFT JOIN Compiled_Parameter ON compiled_id = comp_id
                LEFT JOIN Parameter ON parameter_id = Parameter.id"""
    df_params = pd.read_sql_query(query, engine)
    return df_params

# Cell
def get_table(engine, table_name):
    query = """SELECT * FROM """+str(table_name)
    df_table = pd.read_sql_query(query, engine)
    return df_table

# Cell
def stim_param_to_dict(param_df, md5):
    param_dict = {}
    stim_mask = param_df["hash"] == md5
    for _, row in param_df[stim_mask][["param_name", "param_value"]].iterrows():
        try:
            param = json.loads(row["param_value"])
        except:
            param = row["param_value"]
        param_dict[row["param_name"]] = param
    return param_dict