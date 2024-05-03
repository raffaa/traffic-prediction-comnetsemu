import random
import time


def generate_traffic(net):
    # Starting iperf server on hosts
    for host in  net.hosts:
        h = net.get(host.name)
        h.cmd("iperf -s &")

    # Starting iperf client on other hosts
    for host in  net.hosts:
        for other_host in net.hosts:
            if other_host != host:
                bandwidth = random.randint(10, 100) # Random bandwidth between 10 and 100 Mbps
                h = net.get(host.name)
                h.cmd("iperf -c {other_host.IP} -b {bandwidth}M &")

    # Keep running indefinitely
    while True:
        time.sleep(1)