#! /usr/bin/env python

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
                    default="results/1542628139")

args = parser.parse_args()
path = os.path.abspath(args.dir)

os.chdir(path)

for file in os.listdir('.'):
    print file
    if str(file)=='default-1542891097-offload-on-result':
        test_run = 'A'
        data[test_run] = getPLT(file)
    if str(file)=='bpf.iw20-1542843374.exclude_aliexpress-result':
        test_run = 'B'
        data[test_run] = getPLT(file)
    if str(file)=='bpf.iw40-1542878757-offload-on-result':
        test_run = 'C'
        data[test_run] = getPLT(file)


#################################
####    H2 speed up plot    #####

fig, ax = plt.subplots()

print "get the speed up value for each site"
speed_upB = {}
speed_upC = {}

i=0

# common_sites = intersect( data['default'].keys(), data['iw20'].keys() )
for site in sorted(data['B'].keys()):
    speed_upB[site] = np.array(data['A'][site]).mean() - np.array(data['B'][site]).mean()
    speed_upC[site] = np.array(data['A'][site]).mean() - np.array(data['C'][site]).mean()

    # if speed_up[site] < 0:
    # print i, '%40s' % site, '%6d' % int(round(speed_up[site])), 
    # print '\t', data['A'][site], '\t', data['B'][site]
    i+=1

x = np.sort(speed_upB.values())
cdf=np.arange(len(x))/float(len(x))
ax.plot( x, cdf, lw=2, ls ='--', label = 'speed up of IW20 vs. IW10')

x = np.sort(speed_upC.values())
cdf=np.arange(len(x))/float(len(x))
ax.plot( x, cdf, lw=2, ls ='-', label = 'speed up of IW40 vs. IW10')

# ax.set_xscale('log')
ax.set_xlim(xmin=-600,xmax=600)
ax.set_ylim(ymin=0    ,ymax=1)
plt.grid(ls='dotted')


plt.xlabel('PLT speed-up (ms)', fontsize=17)
plt.ylabel('CDF (Difference)', fontsize=17)
plt.legend(loc='best')

plt.savefig('IW_speedup.pdf')

plt.show()