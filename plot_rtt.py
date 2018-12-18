#! /usr/bin/env python

# For CC option experiment

# INPUT: packet traces: ./{cubic/reno/bbr/vegas}/dump_server
# OUTPUT: plot of RTT evolution, using tcptrace

import os
from subprocess import call
import numpy as np
import matplotlib.pyplot as plt

import argparse
parser = argparse.ArgumentParser(description="Get RTTs from TCPtrace's RTT graph")

parser.add_argument('--dir', '-d', default="trace-cc")
parser.add_argument('--all', '-a', help="analyse all connections in folder", default= False, action='store_true')
parser.add_argument('--verbose','-v', default= False, action='store_true')
args = parser.parse_args()


MARK = 0
TIME = 1 	# column No
VALUE= 2

rtt = {}

linestyles = ['--','-',':','-.']
# linesizes =  [1,1,1,1]
# markers    = ['.','^','+' ,'d']

def loadRTT(dir, rttfile):

	RTTs=[]

	file = str(dir) + rttfile
	if not os.path.isfile(file):
		return(0)
	for line in open(file ,'r'):
		if line.startswith('dot'):
			l = line.strip().split(' ')
			rtt_val = float(l[VALUE])
			timestamp= float(l[TIME])
			RTTs.append([timestamp, rtt_val])
	return RTTs

def plot_rtt_PDF(data, side):

	fig, ax = plt.subplots()

	x=np.sort(data)

	cdf=np.arange(len(x))/float(len(x))
	ax.plot( x, cdf, label='Round-trip time')

	# ax.set_xscale('log')

	ax.legend()
	plt.show()
	plt.savefig(str(side)+'rtt-cdf.eps', bbox_inches='tight')


def plot_rtt(data, side):

	fig, ax = plt.subplots()
	i = 0

	# for cc in data:
	for cc in ['reno','cubic','bbr','vegas']:
		rtt_cc = data[cc]
		# to unzip list of tuples
		# see stackoverflow.com/q/36901/2703937
		series = zip(*rtt_cc)
		x = np.array(series[0])
		x -= x[0]
		ax.plot( x, series[1], label=str(cc), linestyle=linestyles[i])
		# ax.plot( x, series[1], label=str(cc), linestyle=linestyles[i], marker=markers[i])
		i += 1

	ax.legend()
	plt.xlabel('Time lapsed (sec)')
	plt.ylabel('Round-trip time (msec)')
	# plt.grid(ls='dotted')
	plt.grid()
	# plt.show()
	plt.savefig(str(side)+'-rtt-cc.pdf', bbox_inches='tight')
	plt.savefig(str(side)+'-rtt-cc.png', bbox_inches='tight')


# from RichieHindle, stackoverflow
def immediate_subdir(a_dir):
	print os.listdir(a_dir)
	return [name for name in sorted(os.listdir(a_dir))
		if os.path.isdir(os.path.join(a_dir, name))]


def main(dir):
	jitter = []
	os.chdir(dir)
	print os.listdir('./')

	for cc in immediate_subdir('./'):
		os.chdir(cc)
		# extract RTT from trace
		tcptrace = 'tcptrace -R  -n ./dump_server'
		print cc, tcptrace
		call(tcptrace +'> /dev/null', shell=True)

		os.chdir("..")
		# server side RTT
		rtt[cc] =loadRTT(cc, '/b2a_rtt.xpl')
		print os.getcwd()

	plot_rtt(rtt,"server")

if __name__ == '__main__':
	dir = args.dir
	main(dir)