#! /usr/bin/env python

# INPUT: iperf3 json
#   ./stress_test/client-*  (.json)
#   ./stress_test/server-*  (.json)
#   ./stress_test/bpf-client-*  (.json)
#   ./stress_test/bpf-server-*  (.json)

# OUTPUT:
# plot rate of all client->server tests or server->client tests

import os
import pprint
import socket
import argparse

# try to use simplejson - 3 times faster than original json package
try:
    import simplejson as json
except ImportError:
    import json


parser = argparse.ArgumentParser(description="plot iperf test results from json")
parser.add_argument('--expdir', '-d',
                    help="Directory to store results",
                    default="delay-ack")

args = parser.parse_args()

exp_dir = args.expdir

if exp_dir[-1] != '/':
    exp_dir+='/'


def get_intervals(node):
    bitrate = []
    rtt     = {}

    for interval in node["intervals"]:

        if len(interval["subflows"]) == 1:
            ival = interval["subflows"][0]
            bitrate.append((ival["start"], float(ival["bits_per_second"]) / (1024768) ))

    return(bitrate, rtt)


def get_each_testrun(test_run):
    # in Mbps
    bitrate=float(test_run["end"]["streams"][0]["sender"]["bits_per_second"])/(1 << 20)
    rtt    =float(test_run['end']['streams'][0]['sender']["mean_rtt"])
    return(bitrate, rtt)


################
####  Plot  ####

import numpy as np
import matplotlib.pyplot as plt

def get_results_of_testtype(test_type):
    rtts=[]
    bitrates=[]
    for file in os.listdir(exp_dir):
        if not file.endswith(".json"):
            continue

        if ((file.startswith("client") and  test_type == "baseline")
        or (file.startswith("1seg-client") and test_type == "1seg")
        or (file.startswith("10segs-quarterRTT-client") and test_type == "10segs-quarterRTT")
        or (file.startswith("100segs-halfRTT-client") and test_type == "100segs-halfRTT")):
            print(file)
            pass
        else:
            continue

        with open(exp_dir+file) as data_file:

            test_run = json.load(data_file)

            bitrate, rtt = get_each_testrun(test_run)
            # bitrate, rtt = get_intervals(test_run)

            rtts.append(rtt)
            bitrates.append(bitrate)

    return (rtts, bitrates)


from textwrap import wrap

def plot_box_graph():

    data = []
    rtt_data = []

    xlabel = 'Overhead of TCP Option Extended Operations vs. Baseline'

    labels = ['Baseline',"every 1 MSS", '10 MSS or 1/4 RTT',"100 MSS or 1/2 RTT"]
    labels = [ '\n'.join(wrap(l, 18)) for l in labels ]

    for test_type in ['baseline',"1seg", '10segs-quarterRTT',"100segs-halfRTT"]:
        rtts, bitrates = get_results_of_testtype(test_type)
        print test_type, np.mean(bitrates), np.mean(rtts)
        data.append(bitrates)
        rtt_data.append(rtts)


    ####################
    print("plot bitrate")
    fig, ax = plt.subplots()
    ax.boxplot(data)

    ax.set_xticklabels(labels)
    # plt.xticks(rotation=45)
    ax.set_ylim([0,5])

    # plt.xlabel(xlabel)
    plt.ylabel('TCP Throughput Measured by iPerf3 (Mbps)')

    plt.grid(linestyle='dotted')
    plt.tight_layout()
    plt.show()
    plt.savefig(exp_dir + 'delayack-tput.pdf')


    ###################
    # print("plot rtt")
    # fig, ax = plt.subplots()
    # ax.boxplot(rtt_data)

    # ax.set_xticklabels(labels)
    # # plt.xticks(rotation=45)
    # ax.set_ylim([0,100])

    # # plt.xlabel(xlabel)
    # plt.ylabel('Round-Trip Time Measured by iPerf3 (micro-seconds)')

    # plt.grid(linestyle='dotted')
    # plt.tight_layout()

    # plt.savefig(exp_dir + 'overhead-rtt.pdf')

plot_box_graph()
