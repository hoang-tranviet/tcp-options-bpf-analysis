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
                    help="Directory which contains results",
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
    bitrate=float(test_run["end"]["streams"][0]["sender"]["bits_per_second"])/(1000000000)
    rtt    =float(test_run['end']['streams'][0]['sender']["mean_rtt"])
    local_cpu = float(test_run['end']['cpu_utilization_percent']['host_total'])
    remote_cpu = float(test_run['end']['cpu_utilization_percent']['remote_total'])
    return(bitrate, rtt, local_cpu, remote_cpu)


################
####  Plot  ####

import numpy as np
import matplotlib.pyplot as plt

def get_results_of_testtype(test_type):
    rtts=[]
    bitrates=[]
    local_cpus = []
    remote_cpus = []
    for file in os.listdir(exp_dir):
        if not file.endswith(".json"):
            continue

        if ((file.startswith("client") and  test_type == "baseline")
        or (file.startswith("insert-client") and test_type == "option-insert")
        or (file.startswith("insert-parse-client-") and test_type == "option-insert-parse")
        or (file.startswith("insert-parse-sockopt-client-") and test_type == "option-insert-parse-sockopt")):
            # print(file)
            pass
        else:
            continue

        with open(exp_dir+file) as data_file:

            test_run = json.load(data_file)

            bitrate, rtt, local_cpu, remote_cpu = get_each_testrun(test_run)
            # bitrate, rtt = get_intervals(test_run)

            rtts.append(rtt)
            bitrates.append(bitrate)
            local_cpus.append(local_cpu)
            remote_cpus.append(remote_cpu)

    return (rtts, bitrates, local_cpus, remote_cpus)


from textwrap import wrap

def plot_box_graph():

    data = []
    rtt_data = []
    lcpu_data = []
    rcpu_data = []

    xlabel = 'Overhead of TCP Option Extended Operations vs. Baseline'

    labels = ['Baseline','Insert','Insert and Parse','Insert and Parse and BPF-Setsockopt']
    labels = [ '\n'.join(wrap(l, 18)) for l in labels ]

    for test_type in ['baseline','option-insert','option-insert-parse','option-insert-parse-sockopt']:
        rtts, bitrates, local_cpus, remote_cpus = get_results_of_testtype(test_type)
        print np.mean(bitrates), np.mean(rtts), np.mean(local_cpus), np.mean(remote_cpus), test_type
        data.append(bitrates)
        rtt_data.append(rtts)
        lcpu_data.append(local_cpus)
        rcpu_data.append(remote_cpus)


    ####################
    print("plot bitrate")
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.boxplot(data)

    ax.set_xticklabels(labels)
    # plt.xticks(rotation=45)
    ax.set_ylim([9,9.5])

    # plt.xlabel(xlabel)
    # plt.ylabel('TCP Throughput (Gbps)')

    plt.grid(linestyle='dotted')
    plt.tight_layout()
    # plt.show()
    plt.savefig(exp_dir + 'overhead-tput.pdf')
    plt.savefig(exp_dir + 'overhead-tput.png')


    ###################
    print("plot rtt")
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.boxplot(rtt_data)

    ax.set_xticklabels(labels)
    # plt.xticks(rotation=45)
    ax.set_ylim([400,500])

    # plt.xlabel(xlabel)
    # plt.ylabel('Round-Trip Time (us)')

    plt.grid(linestyle='dotted')
    plt.tight_layout()
    # plt.show()

    plt.savefig(exp_dir + 'overhead-rtt.pdf')
    plt.savefig(exp_dir + 'overhead-rtt.png')


    ###################
    print("CPU usage")
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.boxplot(lcpu_data)

    ax.set_xticklabels(labels)
    # ax.set_ylim([0,30])

    # plt.xlabel(xlabel)
    # plt.ylabel("Sender's CPU usage (%)")

    plt.grid(linestyle='dotted')
    plt.tight_layout()
    # plt.show()

    plt.savefig(exp_dir + 'overhead-local-cpu.pdf')
    plt.savefig(exp_dir + 'overhead-local-cpu.png')

    ###################
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.boxplot(rcpu_data)

    ax.set_xticklabels(labels)
    # ax.set_ylim([0,50])

    # plt.xlabel(xlabel)
    # plt.ylabel("Receiver's CPU usage (%)")

    plt.grid(linestyle='dotted')
    plt.tight_layout()
    # plt.show()

    plt.savefig(exp_dir + 'overhead-remote-cpu.pdf')
    plt.savefig(exp_dir + 'overhead-remote-cpu.png')

plot_box_graph()
