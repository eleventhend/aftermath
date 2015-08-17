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

def encounter(m, p, rerolls, die, success):
    """
    encounter processes a single rool of a dice pool comparing it against the 
        outcomes needed to perform a desired maneuver
    """
    pool = p.copy()
    maneuver = m.copy()
    for x in xrange(0, (rerolls+1)):
        for i in ['combat', 'social', 'skill', 'wild']:
            for k in xrange(0, pool['count'].loc[i]):
                roll = roller(die)
                maneuver['count'].loc[i, roll] += 1
        pool['count'] = 0
        for j in xrange(0, len(maneuver)):
            if maneuver['count'][j] == maneuver['required'][j]:
                maneuver['result'][j] = 1
            elif maneuver['count'][j] >= maneuver['required'][j]:
                maneuver['result'][j] = 1
                pool['count'][j/die] += (maneuver['count'][j] - 
                    maneuver['required'][j])
                maneuver['count'][j] = maneuver['required'][j]
        #wizardry below
        if maneuver.sum()[2] == (die*3):
            success += 1
            return success
    return success

"""
command line arguments
    Currently only sets dice pips
"""
parser = argparse.ArgumentParser(
    description='Run Monte Carlo simulations for Aftermath Engine', 
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--pips", type=int, default=6,
    help="Optional: set the dice pips for the dice in pool/maneuver")
parser.add_argument("--rerolls", type=int, default=0,
    help="Optional: set the number of rerolls allowed for the player's pool")
parser.add_argument("--n", type=int, default=10000,
    help="Optional: set the number of samples for the Monte Carlo simulation")
args = parser.parse_args()
die = args.pips
rerolls = args.rerolls
sample = args.n

"""
die_type should be a hierarchical index on one side of color
    (not clear by mechanics which side yet)

Create dice pool & populate it with available dice (=player default dice pool)
    'count' - the number of dice available in pool
"""
pool = pd.DataFrame(index=('combat', 'social', 'skill', 'wild'), 
    columns=('count',))
pool['count'] = (4, 1, 3, 0)
d_type = ('combat', 'social', 'skill')
d_pips = range(1, die+1)

"""
Create maneuver & populate with maneuver requirements
    'required' - the number of dice of that pip required for a maneuver
"""
midx = pd.MultiIndex.from_tuples(list(itertools.product(d_type, d_pips)))
default_maneuver = pd.DataFrame(0, index=midx, 
    columns=('required','count','result'))

inertial_purge = default_maneuver.copy()
inertial_purge['required'].loc['combat', 1] = 1
inertial_purge['required'].loc['combat', 6] = 2
inertial_purge['required'].loc['skill', 6] = 1

#init success as 0 in decimal form
success = 0.0
#run samples
for x in xrange(0, sample):
    success = encounter(inertial_purge, pool, rerolls, die, success)

print ("%(y)s/%(s)s succeeded after %(r)s rerolls" 
    %{"y": int(success), "s": sample, "r": rerolls})
print ("%(p)s%% success rate after %(r)s rerolls" 
    %{"p": ((success/sample)*100), "r": rerolls})
