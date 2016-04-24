# import matplotlib.pyplot as plt
import pylab as pl
import numpy as np
import pandas as pd
import seaborn


""" Makes a Radar class and a function to create radar graphs later """


class Radar(object):
    def __init__(self, fig, titles, labels, rect=None):
        if rect is None:
            rect = [0.05, 0.05, 0.95, 0.95]

        self.n = len(titles)
        self.angles = np.arange(90, 90+360, 360.0/self.n)
        self.axes = [fig.add_axes(rect, projection="polar", label="axes%d" % i) for i in range(self.n)]

        self.ax = self.axes[0]
        self.ax.set_thetagrids(self.angles, labels=titles, fontsize=14)

        for ax in self.axes[1:]:
            ax.patch.set_visible(False)
            ax.grid("off")
            ax.xaxis.set_visible(False)

        for ax, angle, label in zip(self.axes, self.angles, labels):
            ax.set_rgrids(range(20, 100, 20), angle=angle, labels=label)
            ax.spines["polar"].set_visible(False)
            ax.set_ylim(0, 100)

    def plot(self, values, *args, **kw):
        angle = np.deg2rad(np.r_[self.angles, self.angles[0]])
        values = np.r_[values, values[0]]
        self.ax.plot(angle, values, *args, **kw)

    def get_color(self, i):
        if i == 0:
            return 'c'
        elif i == 1:
            return 'm'
        elif i == 2:
            return 'y'
        elif i == 3:
            return 'g'
        elif i == 4:
            return 'b'
        elif i == 5:
            return 'r'
        else:
            return 'burlywood'


def create_three_point_radar(df, rows=[], size=6):
    fig = pl.figure(figsize=(size, size))

    titles = df.columns

    labels = [range(20, 101, 20) for x in range(len(titles))]

    radar = Radar(fig, titles, labels)

    if rows:
        for i in rows:
            radar.plot(df.values[i],  "-", lw=3, color=radar.get_color(i), alpha=0.4, label=df.index[i])
    else:
        for i in range(len(df.index)):
            radar.plot(df.values[i],  "-", lw=3, color=radar.get_color(i), alpha=0.4, label=df.index[i])
    radar.ax.legend()


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

mind_body_spirit['BODY'] = mind_body_spirit[get_body].sum(axis=1)
mind_body_spirit['MIND'] = mind_body_spirit[get_mind].sum(axis=1)
mind_body_spirit['SPIRIT'] = mind_body_spirit[get_spirit].sum(axis=1)

mind_body_spirit = mind_body_spirit.drop(mind_body_spirit.columns[5:-3], axis=1)


""" Balance by Age created by grouping by age and getting the mean for each
    of mind, body, and spirit as well as the standard deviation of the three.
    Data is graphed here """

balance_by_age = mind_body_spirit.groupby('TEAGE').mean()
balance_by_age.drop(balance_by_age.columns[0:4], axis=1, inplace=True)
balance_by_age = balance_by_age.drop(balance_by_age.index[:3])
ageax = balance_by_age.plot(figsize=(15, 8))
ageax.set_ylabel('Minutes/Day')
ageax.set_xlabel('Age')

stdev_balance_by_age = balance_by_age.copy()
stdev_balance_by_age['STDEV'] = stdev_balance_by_age.std(axis=1)
ax = stdev_balance_by_age.plot(figsize=(15, 8))
ax.set_ylabel('Minutes/Day')
ax.set_xlabel('Age')

""" Sorted by age groups """
labels = ['18-24', '25-34', '35-44', '45-54', '55-64', '65-74', '75+']
balance_by_age['AGEGROUP'] = pd.cut(balance_by_age.index, [18, 25, 35, 45, 55, 65, 75, 86], right=False, labels=labels)

balance_by_agegroup = balance_by_age.groupby('AGEGROUP').mean()
stdev_balance_by_agegroup = balance_by_agegroup.copy()
stdev_balance_by_agegroup['STDEV'] = stdev_balance_by_agegroup.std(axis=1)

agax = stdev_balance_by_agegroup.plot(kind='bar', figsize=(15, 8))
agax.set_ylabel('Minutes/Day')
agax.set_xlabel('Education Level')

for i in range(len(balance_by_agegroup.index)):
    create_three_point_radar(balance_by_agegroup, [i], 6)

create_three_point_radar(balance_by_agegroup, [0, 3, 5], 9)


""" Same format for sorting by children """

balance_by_children = mind_body_spirit.groupby('TRCHILDNUM').mean()
balance_by_children.drop(balance_by_children.columns[0:4], axis=1, inplace=True)
balance_by_children['STDEV'] = balance_by_children.std(axis=1)
childax = balance_by_children.plot(figsize=(15, 8))
childax.set_ylabel('Minutes/Day')
childax.set_xlabel('Number of Children')

""" Data is split for sexes by age """

balance_by_sex = mind_body_spirit.copy()
balance_by_sex.drop(['TUCASEID', 'TRCHILDNUM', "PEEDUCA"], axis=1, inplace=True)
balance_by_sex = balance_by_sex[balance_by_sex.TEAGE >= 18]

balance_by_sex.sort_values(['TEAGE', 'TESEX'])
balance_by_sex = balance_by_sex.groupby(['TESEX', 'TEAGE']).mean()

std_balance_by_sex = balance_by_sex.copy()
std_balance_by_sex['STDEV'] = balance_by_sex.std(axis=1)


maleax = male.plot(title='Male M/B/S balance by age', figsize=(15,8), style=['-','-','-','--'], fontsize=14)
maleax.set_ylabel('Minutes/Day')
maleax.set_xlabel('Age')
femaleax = female.plot(title='Female M/B/S balance by age', figsize=(15,8), style=['-','-','-','--'], fontsize=14)
femaleax.set_ylabel('Minutes/Day')
femaleax.set_xlabel('Age')
