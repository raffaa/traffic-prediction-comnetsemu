import argparse
from traffic_generation import generate_traffic
import csv
import datetime
from os import path, system, listdir
import time
from scapy.all import AsyncSniffer
from scapy.layers.inet import IP, TCP, UDP

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.link import TCLink

parser = argparse.ArgumentParser(description="Network Testing: provide topology and test time")
parser.add_argument("--topo", type=int, default=0, help="Select 0 for simple topology, 1 for complex topology (default 0)")
parser.add_argument("--time", type=int, default=30, help="Duration of the test in seconds (default 30)")
args = parser.parse_args()

#Arguments
TOPOLOGY = args.topo
TEST_TIME = args.time

class SimpleTopology(Topo):
    
    def __init__(self):

        # Initialize topology
        Topo.__init__(self)
        
        # Create templates
        host_config = dict(inNamespace=True)
        link_config = dict()
        host_link_config = dict()

        # Create switch nodes
        for i in range(2):
            sconfig = {"dpid": "%016x" % (i + 1)}
            self.addSwitch("s%d" % (i + 1), **sconfig)


        # Create host nodes
        for i in range(6):
            self.addHost("h%d" % (i + 1), **host_config)

        # Add links
        self.addLink("h1", "s1", **host_link_config)
        self.addLink("h2", "s1", **host_link_config)
        self.addLink("h3", "s1", **host_link_config)
        self.addLink("h4", "s2", **host_link_config)
        self.addLink("h5", "s2", **host_link_config)
        self.addLink("h6", "s2", **host_link_config)

        self.addLink("s1", "s2", **link_config)
 
class ComplexTopology(Topo):
    
    def __init__(self):

        # Initialize topology
        Topo.__init__(self)
        
        # Create templates
        host_config = dict(inNamespace=True)
        link_config = dict()
        host_link_config = dict()

        # Create switch nodes
        for i in range(2):
            sconfig = {"dpid": "%016x" % (i + 1)}
            self.addSwitch("s%d" % (i + 1), **sconfig)

        # Create host nodes
        for i in range(9):
            self.addHost("h%d" % (i + 1), **host_config)

        # Add links
        self.addLink("h1", "s1", **host_link_config)
        self.addLink("h2", "s1", **host_link_config)
        self.addLink("h3", "s1", **host_link_config)
        self.addLink("h4", "s2", **host_link_config)
        self.addLink("h5", "s2", **host_link_config)
        self.addLink("h6", "s2", **host_link_config)
        self.addLink("h7", "s3", **host_link_config)
        self.addLink("h8", "s3", **host_link_config)
        self.addLink("h9", "s3", **host_link_config)

        self.addLink("s1", "s2", **link_config)
        self.addLink("s2", "s3", **link_config)
        self.addLink("s3", "s1", **link_config)
 
topos = { 'simpletopology': (lambda: SimpleTopology()), 'complextopology': (lambda: ComplexTopology()) }

def print_network_configuration(net, file_path):
    with open(file_path, 'w') as file:
        file.write("Hosts:\n")
        for host in net.hosts:
            file.write(f"  {host.name}\n")
            for intf in host.intfList():
                file.write(f"    {intf.name}:\n")
                file.write(f"      IP: {intf.IP()}\n")
                file.write(f"      MAC: {intf.MAC()}\n")
                file.write(f"      Status: {'UP' if intf.isUp() else 'DOWN'}\n")
        
        file.write("\nSwitches:\n")
        for switch in net.switches:
            file.write(f"  {switch.name}\n")
            for intf in switch.intfList():
                file.write(f"    {intf.name}:\n")
                file.write(f"      Status: {'UP' if intf.isUp() else 'DOWN'}\n")
        
        file.write("\nLinks:\n")
        for link in net.links:
            intf1, intf2 = link.intf1, link.intf2
            node1, node2 = intf1.node, intf2.node
            file.write(f"  {node1.name}:{intf1.name} <--> {node2.name}:{intf2.name}\n")
            
start_time = None
def process_packet(packet, csv_file):
    global start_time
    if packet.haslayer("Ethernet") and packet.haslayer("IP"):
        ip_layer = packet.getlayer(IP)
        protocol = ip_layer.payload.name  # Layer 4 protocol name
        
        if start_time is None:
            start_time = packet.time
        elapsed_time = packet.time - start_time

        timestamp = datetime.datetime.fromtimestamp(packet.time).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        src_mac = packet.src
        dst_mac = packet.dst
        src_port, dst_port = "-", "-"

        if protocol == 'TCP':
            tcp_layer = packet.getlayer(TCP)
            src_port = tcp_layer.sport
            dst_port = tcp_layer.dport
        elif protocol == 'UDP':
            udp_layer = packet.getlayer(UDP)
            src_port = udp_layer.sport
            dst_port = udp_layer.dport

        packet_length = len(packet)
        csv_file.write(f"{timestamp},{elapsed_time},{src_mac},{dst_mac},{src_port},{dst_port},{packet_length},{protocol}\n")

def create_csv_files():
    csv_files = {}
    print("[INFO] Building csv files.")
    for iface in listdir("/sys/class/net"):
        operstate_file = path.join("/sys/class/net", iface, "operstate")
        if not path.isfile(operstate_file):
            continue
        with open(operstate_file) as f:
            operstate = f.read().strip()
        if operstate != "up" or iface.startswith("lo") or iface.startswith("enp"):
            continue

        csv_filepath = f"captures/{iface}_packet_traffic.csv"
        csv_file = open(csv_filepath, mode='w', newline='')
        fieldnames = ['Timestamp', 'Elapsed time', 'Source MAC', 'Destination MAC', 'Source Port', 'Destination Port', 'Length', 'Protocol']
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()

        # Associating csv files with interfaces
        csv_files[iface] = csv_file
        
        print(".", end="", flush=True)
    print()

    return csv_files 

def start_capture(csv_files):
    # Start packet sniffer threads for each host
    sniffer_tasks = []
    print("[INFO] Starting capture.")
    for iface, csv_file in csv_files.items():
        sniffer_task = AsyncSniffer(iface=iface, prn=lambda pkt, csvf=csv_file: process_packet(pkt, csvf))
        sniffer_tasks.append(sniffer_task)

    for sniffer in sniffer_tasks:
        sniffer.start()

    return sniffer_tasks

def stop_capture(sniffer_tasks, csv_files):
    print("[INFO] Stopping capture.")
    print("Stopping sniffers:")
    for sniffer in sniffer_tasks:
        sniffer.stop()
        print(".", end="", flush=True)
    print()
    print("Closing csv files:")
    for csv_file in csv_files.values():
        csv_file.close()
        print(".", end="", flush=True)
    print()
    return

def run_topology():

    print("[INFO] Cleaning previous network instances.\n")
    system("sudo mn -c > /dev/null 2>&1 ")
    system("rm -rf ./captures/*.csv")

    controller = RemoteController("c1", ip="127.0.0.1", port=6633)
    topo = ComplexTopology() if TOPOLOGY else SimpleTopology()
    net = Mininet(
        topo=topo,
        switch=OVSKernelSwitch,
        build=False,
        controller=controller,
        autoSetMacs=True,
        autoStaticArp=True,
        link=TCLink,
    )
    net.build()
    net.start()
    time.sleep(1)
    print("\n[INFO] Network started.")
    
    if TOPOLOGY:
        print("[INFO] Starting controller, waiting 40 seconds.")
        system("ryu-manager simple_switch_stp_13.py > /dev/null 2>&1 &")
        print("Running: SimpleSwitch 1.3 STP controller.")
        time.sleep(40)
    else:
        print("[INFO] Starting controller, waiting 3 seconds.")
        system("ryu-manager simple_switch_13.py > /dev/null 2>&1 &")
        print("Running: SimpleSwitch 1.3 controller.")
        time.sleep(3)
    
    print("[INFO] Controller started.")

    print("[INFO] Testing ping connectivity.")
    net.pingAll()
    time.sleep(1)
    print_network_configuration(net, 'network_configuration.txt')
    print("Printed network configuration in network_configuration.txt")
    csv_files = create_csv_files()

    sniffer_tasks = start_capture(csv_files)

    print("[INFO] Starting traffic.")
    generate_traffic(net, TEST_TIME)

    stop_capture(sniffer_tasks, csv_files)
    print("[INFO] Capture stopped.")
    
    # CLI to inspect the network
    # CLI(net)

    # Clean up
    print("[INFO] Stopping network.")
    net.stop()
    system("sudo mn -c > /dev/null 2>&1 ")
    print("[INFO] Clean up done.")

if __name__ == '__main__':
    setLogLevel('info')
    run_topology()