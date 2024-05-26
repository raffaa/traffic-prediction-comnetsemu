import random
import time
import math

def linear_traffic(host1, host2, duration):
    start_time = time.time()
    while time.time() - start_time < duration:
        bandwidth = 1 + (time.time() - start_time) / duration  # Linearly increasing bandwidth
        host1.cmd(f"iperf -c {host2.IP()} -b {bandwidth}M -t 1 &")
        host1.cmd(f"iperf -u -c {host2.IP()} -b {bandwidth}M -t 1 &")  # Adding UDP traffic
        time.sleep(1)

def sinusoidal_traffic(host1, host2, duration):
    start_time = time.time()
    while time.time() - start_time < duration:
        elapsed_time = time.time() - start_time
        bandwidth = 1 + math.sin(2 * math.pi * elapsed_time / duration)  # Sinusoidal bandwidth
        host1.cmd(f"iperf -c {host2.IP()} -b {bandwidth}M -t 1 &")
        host1.cmd(f"iperf -u -c {host2.IP()} -b {bandwidth}M -t 1 &")  # Adding UDP traffic
        time.sleep(1)

def sawtooth_traffic(host1, host2, duration):
    start_time = time.time()
    while time.time() - start_time < duration:
        elapsed_time = time.time() - start_time
        bandwidth = 1 + (elapsed_time % (duration / 10)) / (duration / 10)  # Sawtooth bandwidth
        host1.cmd(f"iperf -c {host2.IP()} -b {bandwidth}M -t 1 &")
        host1.cmd(f"iperf -u -c {host2.IP()} -b {bandwidth}M -t 1 &")  # Adding UDP traffic
        time.sleep(1)

def square_traffic(host1, host2, duration):
    start_time = time.time()
    while time.time() - start_time < duration:
        elapsed_time = time.time() - start_time
        bandwidth = 1 if (elapsed_time % 2 < 1) else 10  # Square wave bandwidth
        host1.cmd(f"iperf -c {host2.IP()} -b {bandwidth}M -t 1 &")
        host1.cmd(f"iperf -u -c {host2.IP()} -b {bandwidth}M -t 1 &")  # Adding UDP traffic
        time.sleep(1)

def constant_traffic(net):
    while True:
        for host in net.hosts:
            for other_host in net.hosts:
                if other_host != host:
                    host.cmd(f"iperf -c {other_host.IP()} -b 1M -t 1 &")
                    host.cmd(f"iperf -u -c {other_host.IP()} -b 1M -t 1 &")  # Adding UDP traffic
        time.sleep(1)

def generate_traffic(net, duration:int):

    # Starting iperf server on hosts
    print("[INFO] Starting servers.")
    for host in  net.hosts:
        host.cmd("iperf -s &")
        print(".", end="", flush=True)
    print()

    # Start constant traffic in the background
    print("[INFO] Starting constant background traffic.")
    constant_traffic_cmd = "while true; do iperf -c {ip} -b 1M -t 1; sleep 1; done &"
    for host in net.hosts:
        for other_host in net.hosts:
            if other_host != host:
                host.cmd(constant_traffic_cmd.format(ip=other_host.IP()))
    
    # Periodic traffic routines
    traffic_routines = [linear_traffic, sinusoidal_traffic, sawtooth_traffic, square_traffic]

    # Sample two random hosts
    host1, host2 = random.sample(net.hosts, 2)
    routine = random.choice(traffic_routines)
    
    print("[INFO] Starting constant background traffic.")
    print(f"Applying {routine.__name__} between {host1.name} and {host2.name}.")
    routine(host1, host2, duration)

    # Wait for the routine to finish
    print("[INFO] Traffic generation completed.")