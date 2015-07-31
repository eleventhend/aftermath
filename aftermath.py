from decimal import *
import random
import itertools

import pandas as pd
import numpy as np

#import plotly.plotly as py
#from plotly.graph_objs import *

def roller(pips):
    draw = range(1, pips+1)
    random.shuffle(draw)
    result = draw[0]
    return result

def encounter(maneuver, pool, die, success):
    maneuver['count'] = 0
    maneuver['result'] = 0
    for i in ['combat', 'social', 'skill', 'wild']:
        for k in range(0, pool['count'].loc[i]):
            roll = roller(die)
            maneuver['count'].loc[i, roll] += 1
    for j in range(0, len(maneuver)):
        if maneuver['count'][j] >= maneuver['required'][j]:
            maneuver['result'][j] = 1
    if maneuver.sum()[2] == (die*3):
        success += 1
    return success

"""
die_type should be a hierarchical index on one side of color
    (not clear by mechanics which side yet)

'count' - the number of dice available in pool
'required' - the number of dice of that pip required for a maneuver

"""
die = 6

pool = pd.DataFrame(index=('combat', 'social', 'skill', 'wild'), 
    columns=('count',))
pool['count'] = (4, 1, 3, 0)

d_type = ('combat', 'social', 'skill')
d_pips = range(1, die+1)
midx = pd.MultiIndex.from_tuples(list(itertools.product(d_type, d_pips)))
default_maneuver = pd.DataFrame(0, index=midx, columns=('required','count'))

inertial_purge = default_maneuver
inertial_purge['required'].loc['combat', 2] = 0
inertial_purge['required'].loc['combat', 6] = 2
inertial_purge['required'].loc['skill', 6] = 2

rerolls = 0
success = 0.0
sample = 10000


for x in range(0, sample):
    success = encounter(inertial_purge, pool, die, success)

print "%(y)s/%(s)s succeeded after %(r)s rerolls" %{"y": int(success), "s": sample, "r": rerolls}
print "%(p)s%% success rate after %(r)s rerolls" %{"p": ((success/sample)*100), "r": rerolls}
