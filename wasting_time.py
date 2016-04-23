import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas import DataFrame, Series
import seaborn


""" Gets the activity summary, renames the case ID field to be consistent with
    other files, and drops the weight column """

activity_summary = pd.read_csv('data/atussum_2014.dat')
activity_summary.drop(activity_summary.columns[1], axis=1, inplace=True)
activity_summary = activity_summary.rename(columns={'tucaseid': 'TUCASEID'})


""" Gets the columns needed for the mind/body/spirit activities list (drops
    any extraneous) """


def get_mbs_activities(i):
    col_names = []
    col_names.append('TUCASEID')
    col_names.append('TRCHILDNUM')
    col_names.append('TEAGE')
    col_names.append('TESEX')
    col_names.append('PEEDUCA')
    col_names.append('PTDTRACE')
    for x in i.columns:
        if x.startswith(('t0102', 't0103', 't1301', 't06', 't120301', 't120312', 't120313', 't120401', 't120102', 't14', 't15', 't120304')):
            col_names.append(x)
    return col_names

col_names = get_mbs_activities(activity_summary)
col_names.remove('t130103')
col_names.remove('t130104')


""" Creates a list of time spent doing all activities for a given category to
    sum later """

get_body = [x for x in col_names if x.startswith(('t0102', 't0103', 't1301'))]
get_mind = [x for x in col_names if x.startswith(('t06', 't120301', 't120312', 't120313', 't120401', 't120102'))]
get_spirit = [x for x in col_names if x.startswith(('t14', 't15', 't120304'))]


""" Create the frame and add columns with the sum of time spent doing each
    type of activity, then clean the unneeded columns """

mind_body_spirit = activity_summary[col_names].copy()
mind_body_spirit.head()

mind_body_spirit['BODY_TOTAL'] = mind_body_spirit[get_body].sum(axis=1)
mind_body_spirit['MIND_TOTAL'] = mind_body_spirit[get_mind].sum(axis=1)
mind_body_spirit['SPIRIT_TOTAL'] = mind_body_spirit[get_spirit].sum(axis=1)

mind_body_spirit = mind_body_spirit.drop(mind_body_spirit.columns[5:-3], axis=1)


""" Balance by Age created by grouping by age and getting the mean for each
    of mind, body, and spirit. Data is graphed here """

balance_by_age = mind_body_spirit.groupby('TEAGE').mean()
balance_by_age.drop(balance_by_age.columns[0:4], axis=1, inplace=True)
balance_by_age.plot()

""" Same format for sorting by children, sex, education level"""
balance_by_children = mind_body_spirit.groupby('TRCHILDNUM').mean()
balance_by_children.drop(balance_by_children.columns[0:4], axis=1, inplace=True)
balance_by_children.plot()

balance_by_sex = mind_body_spirit.groupby('TESEX').mean()
balance_by_sex.drop(balance_by_sex.columns[0:4], axis=1, inplace=True)
balance_by_sex.plot(kind='barh')

balance_by_edu = mind_body_spirit.groupby('PEEDUCA').mean()
balance_by_edu.drop(balance_by_edu.columns[0:4], axis=1, inplace=True)
balance_by_edu.plot(kind='bar')
