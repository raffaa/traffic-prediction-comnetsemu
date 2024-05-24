import random
import time


def generate_traffic(net, duration:int):
    start_time = time.time()
    
    # Starting iperf server on hosts
    print("starting servers")
    for host in  net.hosts:
        host.cmd("iperf -s &")
    time.sleep(3)
    print("starting traffic")
    # Generate traffic for the specified duration
    while time.time() - start_time < duration:
        for host in  net.hosts:
            for other_host in net.hosts:
                if other_host != host:
                    bandwidth = random.randint(1,10) # Random bandwidth between 1 and 10 Mbps
                    host.cmd(f"iperf -c {other_host.IP()} -b {bandwidth} &")
                time.sleep(1)
    

    # Stop iperf servers
    # for host in net.hosts:
    #     h = net.get(host.name)
    #     h.cmd("killall -9 iperf")

    #print("Traffic generation completed.")