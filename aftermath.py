from decimal import *
import random
import itertools
import argparse


import pandas as pd
import numpy as np

#import plotly.plotly as py
#from plotly.graph_objs import *

def roller(pips):
    #rolls a pips sided die, returns the result
    draw = range(1, pips+1)
    random.shuffle(draw)
    result = draw[0]
    return result

def encounter(maneuver, pool, die, success):
    """
    encounter processes a single rool of a dice pool comparing it against the 
        outcomes needed to perform a desired maneuver
    """
    for i in ['combat', 'social', 'skill', 'wild']:
        for k in xrange(0, pool['count'].loc[i]):
            roll = roller(die)
            maneuver['count'].loc[i, roll] += 1
    for j in xrange(0, len(maneuver)):
        if maneuver['count'][j] >= maneuver['required'][j]:
            maneuver['result'][j] = 1
    if maneuver.sum()[2] == (die*3):
        success += 1
    return success

#command line arguments
parser = argparse.ArgumentParser(
    description='Run Monte Carlo simulations for Aftermath Engine', 
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--pips", type=int, default=6,
    help="Optional: set the dice pips for the dice in pool/maneuver")
args = parser.parse_args()

#Set dice pips (default 6)
die = args.pips

"""
die_type should be a hierarchical index on one side of color
    (not clear by mechanics which side yet)

'count' - the number of dice available in pool
'required' - the number of dice of that pip required for a maneuver
"""

#Create dice pool & populate it with available dice (=player default dice pool)
pool = pd.DataFrame(index=('combat', 'social', 'skill', 'wild'), 
    columns=('count',))
pool['count'] = (4, 1, 3, 0)


d_type = ('combat', 'social', 'skill')
d_pips = range(1, die+1)
midx = pd.MultiIndex.from_tuples(list(itertools.product(d_type, d_pips)))
default_maneuver = pd.DataFrame(0, index=midx, columns=('required','count','result'))

inertial_purge = default_maneuver
inertial_purge['required'].loc['combat', 2] = 0
inertial_purge['required'].loc['combat', 6] = 2
inertial_purge['required'].loc['skill', 6] = 2

#init success as 0 in decimal form
success = 0.0
#set rerolls allowed by engine
rerolls = 0
#set number of samples to be run
sample = 10000

#run samples
for x in xrange(0, sample):
    inertial_purge['count'] = 0
    inertial_purge['result'] = 0
    success = encounter(inertial_purge, pool, die, success)

print "%(y)s/%(s)s succeeded after %(r)s rerolls" %{"y": int(success), "s": sample, "r": rerolls}
print "%(p)s%% success rate after %(r)s rerolls" %{"p": ((success/sample)*100), "r": rerolls}
