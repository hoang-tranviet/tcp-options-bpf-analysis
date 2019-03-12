#! /usr/bin/env python

# For overhead/stress test experiment

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
                    default="")

args = parser.parse_args()

exp_dir = args.expdir

if exp_dir[-1] != '/':
    exp_dir.append('/')


def get_intervals(node):
    bitrate = []
    rtt     = {}

    for interval in node["intervals"]:

        if len(interval["subflows"]) == 1:
            ival = interval["subflows"][0]
            bitrate.append((ival["start"], float(ival["bits_per_second"]) / (1024768) ))

    return(bitrate, rtt)


def get_each_testrun(test_run):
    # in Gbps
    bitrate=float(test_run["end"]["streams"][0]["sender"]["bits_per_second"])/(1 << 30)
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
        or (file.startswith("insert-client") and test_type == "option-insert")
        or (file.startswith("insert-parseclient-") and test_type == "option-insert-parse")
        or (file.startswith("insert-parse-sockopt-client-") and test_type == "option-insert-parse-sockopt")):
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

    labels = ['Baseline','Insert','Insert and Parse','Insert and Parse and BPF-Setsockopt']
    labels = [ '\n'.join(wrap(l, 18)) for l in labels ]

    for test_type in ['baseline','option-insert','option-insert-parse','option-insert-parse-sockopt']:
        rtts, bitrates = get_results_of_testtype(test_type)
        print np.mean(bitrates), np.mean(rtts), test_type
        data.append(bitrates)
        rtt_data.append(rtts)


    ####################
    print("plot bitrate")
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.boxplot(data)

    ax.set_xticklabels(labels)
    # plt.xticks(rotation=45)
    ax.set_ylim([20,40])

    # plt.xlabel(xlabel)
    plt.ylabel('TCP Throughput (Gbps)')

    plt.grid(linestyle='dotted')
    plt.tight_layout()
    # plt.show()
    plt.savefig(exp_dir + 'overhead-tput.pdf')


    ###################
    print("plot rtt")
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.boxplot(rtt_data)

    ax.set_xticklabels(labels)
    # plt.xticks(rotation=45)
    ax.set_ylim([20,40])

    # plt.xlabel(xlabel)
    plt.ylabel('Round-Trip Time (micro-seconds)')

    plt.grid(linestyle='dotted')
    plt.tight_layout()

    plt.savefig(exp_dir + 'overhead-rtt.pdf')

plot_box_graph()
