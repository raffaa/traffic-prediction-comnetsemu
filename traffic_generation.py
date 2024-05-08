import random
import time


def generate_traffic(net, duration):
    start_time = time.time()
    
    # Starting iperf server on hosts
    for host in  net.hosts:
        host.cmd("iperf -s &")

    # Generate traffic for the specified duration
    while time.time() - start_time < duration:
        for host in  net.hosts:
            for other_host in net.hosts:
                if other_host != host:
                    bandwidth = random.randint(1, 10) # Random bandwidth between 10 and 100 Mbps
                    host.cmd(f"iperf -c {other_host.IP()} -b {bandwidth}M  &")
        time.sleep(1)  # Sleep for 1 second before generating traffic again

    # Stop iperf servers
    # for host in net.hosts:
    #     h = net.get(host.name)
    #     h.cmd("killall -9 iperf")

    print("Traffic generation completed.")