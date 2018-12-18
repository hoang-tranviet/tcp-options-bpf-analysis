#! /usr/bin/env python

# For IW option experiment

# INPUT: results/{test_type}/{epoch_time}  created by epload

# OUTPUT:
# PLT (onLoad) time of all sites

import os
import argparse
from subprocess import call
import numpy as np
import matplotlib.pyplot as plt

def getPLT(epload_file):
    onLoad = {}
    # test_run='iw=10' or iw=20
    for line in open(epload_file):
        if '[page file]' in line:
            site = (line.split())[-1]
            # print site,
        # initialize the value list
        if site not in onLoad:
            onLoad[site] = []

        if '[page load time]' in line:
            val = (line.split())[-1]
            # print val
            onLoad[site].append(int(float(val)))
    return onLoad

data = {}

parser = argparse.ArgumentParser(
                    description="collect and plot onLoad time from epload output files")
parser.add_argument('--dir', '-d',
                    help="Directory contains data",
                    default="results/")

args = parser.parse_args()
path = os.path.abspath(args.dir)

os.chdir(path)

for file in os.listdir('.'):
    print file
    if str(file)=='default-1542891097-result':
        test_run = '10'
        data[test_run] = getPLT(file)
    if str(file)=='iw20-1542843374-result':
        test_run = '20'
        data[test_run] = getPLT(file)
    if str(file)=='iw40-1542878757-result':
        test_run = '40'
        data[test_run] = getPLT(file)
    if str(file)=='iw4-1544306352-result':
        test_run = '4'
        data[test_run] = getPLT(file)
    if str(file)=='iw2-1544310518-result':
        test_run = '2'
        data[test_run] = getPLT(file)


#################################
####    Relative PLT plot    ####

iw_list = ['2','4','10','20','40']

linestyles = ['-','-','--','-','-']
markers    = ['.' ,'^', '' ,'' ,'+']

speed_up ={}

print "get the relative PLT value for each site"

fig, ax = plt.subplots()
i=0
l=0

# common_sites = intersect( data['default'].keys(), data['iw20'].keys() )
for iw in iw_list:
    speed_up[iw] = {}

    for site in sorted(data['20'].keys()):
        speed_up[iw][site] = np.array(data[iw][site]).mean() - np.array(data['10'][site]).mean()

        # if speed_up[site] < 0:
        # print i, '%40s' % site, '%6d' % int(round(speed_up[site])), 
        # print '\t', data['A'][site], '\t', data['B'][site]
        i+=1

    x = np.sort(speed_up[iw].values())
    cdf=np.arange(len(x))/float(len(x))
    ax.plot( x, cdf, lw=2, ls =linestyles[l], marker = markers[l], markevery=10, label = 'IW' + iw + ' vs. IW10')
    l+=1

# ax.set_xscale('log')
ax.set_xlim(xmin=-600,xmax=600)
ax.set_ylim(ymin=0    ,ymax=1)
plt.grid(ls='dotted')

plt.xlabel('Relative PLT to IW10 (ms)')
plt.ylabel('CDF (Difference)')
plt.tight_layout()
plt.legend(loc='best')

plt.savefig('IW_speedup.pdf')

plt.show()