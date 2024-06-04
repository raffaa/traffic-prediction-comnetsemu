import random
import time
import math
SCALE = 0.5

def linear_traffic(host1, host2, start_time, current_time, duration):
    elapsed_time = current_time - start_time
    bandwidth = 1 + elapsed_time / duration  # Linearly increasing 
    bandwidth = bandwidth * SCALE
    host1.cmd(f"iperf -c {host2.IP()} -b {bandwidth}M -t 1 &")
    host1.cmd(f"iperf -u -c {host2.IP()} -b {bandwidth}M -t 1 &")  # Adding UDP traffic

def sinusoidal_traffic(host1, host2, start_time, current_time, duration):
    elapsed_time = current_time - start_time
    bandwidth = 1 + math.sin(2 * math.pi * elapsed_time / duration)  # Sinusoidal bandwidth
    bandwidth = bandwidth * SCALE
    host1.cmd(f"iperf -c {host2.IP()} -b {bandwidth}M -t 1 &")
    host1.cmd(f"iperf -u -c {host2.IP()} -b {bandwidth}M -t 1 &")  # Adding UDP traffic

def sawtooth_traffic(host1, host2, start_time, current_time, duration):
    elapsed_time = current_time - start_time
    bandwidth = 1 + (elapsed_time % (duration / 10)) / (duration / 10)  # Sawtooth bandwidth
    bandwidth = bandwidth * SCALE
    host1.cmd(f"iperf -c {host2.IP()} -b {bandwidth}M -t 1 &")
    host1.cmd(f"iperf -u -c {host2.IP()} -b {bandwidth}M -t 1 &")  # Adding UDP traffic

def square_traffic(host1, host2, start_time, current_time, duration):
    elapsed_time = current_time - start_time
    bandwidth = 1 if (elapsed_time % 2 < 1) else 10  # Square wave bandwidth
    bandwidth = bandwidth * SCALE
    host1.cmd(f"iperf -c {host2.IP()} -b {bandwidth}M -t 1 &")
    host1.cmd(f"iperf -u -c {host2.IP()} -b {bandwidth}M -t 1 &")  # Adding UDP traffic

def constant_traffic(net):
    for host in net.hosts:
        for other_host in net.hosts:
            if other_host != host:
                host.cmd(f"iperf -c {other_host.IP()} -b 1M -t 1 &")
                host.cmd(f"iperf -u -c {other_host.IP()} -b 1M -t 1 &")  # Adding UDP traffic

def cleanup(net):
    for host in net.hosts:
        host.cmd("killall -9 iperf")
    print("Cleanup complete.")

def generate_traffic(net, duration:int):
    random.seed(time.time())
    
    # Starting iperf server on hosts
    print("[INFO] Starting servers.")
    for host in  net.hosts:
        host.cmd("iperf -s &")
        print(".", end="", flush=True)
    print()
 
    # Periodic traffic routines
    traffic_routines = [linear_traffic, sinusoidal_traffic, sawtooth_traffic, square_traffic]

    # Sample two random hosts
    host1, host2 = random.sample(net.hosts, 2)
    routine = random.choice(traffic_routines)
    
    print("Generic constant traffic running in the background.")
    print(f"Applying {routine.__name__} between {host1.name} and {host2.name}.")
    
    # Traffic generation loop
    start_time = time.time()
    while time.time() - start_time < duration:
        current_time = time.time()
        
        # Generate constant background traffic
        constant_traffic(net)
        
        # Generate periodic traffic
        routine(host1, host2, start_time, current_time, duration)

        time.sleep(1)

    # Cleanup
    cleanup(net)

    # Wait for the routine to finish
    print("[INFO] Traffic generation completed.")