from traffic_generation import generate_traffic
import csv
import datetime
from os import path, system, listdir
import asyncio
from scapy.all import AsyncSniffer
from scapy.layers.inet import IP, TCP, UDP

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.link import TCLink

class CustomTopology(Topo):
    
    def __init__( self ):

        # Initialize topology
        Topo.__init__( self )
        
        # Create router node
        s1 = self.addSwitch("s1")

        # Create host nodes
        h1 = self.addHost("h1")
        h2 = self.addHost("h2")

        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
 
topos = { 'customtopology': ( lambda: CustomTopology() ) }

async def packet_sniffer(iface, csv_file):
    sniffer = AsyncSniffer(iface=iface, prn=lambda pkt: process_packet(pkt, csv_file))
    sniffer.start()
    await asyncio.sleep(30)  # Adjust the time as needed
    sniffer.stop()

start_time = None
def process_packet(packet, csv_file):
    global start_time
    if packet.haslayer("Ethernet") and packet.haslayer("IP"):
        ip_layer = packet.getlayer(IP)
        protocol = ip_layer.payload.name  # Get the name of the layer 4 protocol
        
        if start_time is None:
            start_time = packet.time
        elapsed_time = packet.time - start_time

        timestamp = datetime.datetime.fromtimestamp(packet.time).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        src_mac = packet.src
        dst_mac = packet.dst
        if protocol == 'TCP':
            tcp_layer = packet.getlayer(TCP)
            src_port = tcp_layer.sport
            dst_port = tcp_layer.dport
            packet_length = len(packet)
            csv_file.write(f"{timestamp},{elapsed_time},{src_mac},{dst_mac},{src_port},{dst_port},{packet_length},{protocol}\n")
        elif protocol == 'UDP':
            udp_layer = packet.getlayer(UDP)
            src_port = udp_layer.sport
            dst_port = udp_layer.dport
            packet_length = len(packet)
            csv_file.write(f"{timestamp},{elapsed_time},{src_mac},{dst_mac},{src_port},{dst_port},{packet_length},{protocol}\n")
        else:
            packet_length = len(packet)
            csv_file.write(f"{timestamp},{elapsed_time},{src_mac},{dst_mac},-,-,{packet_length},{protocol}\n")

async def run_topology():
    system("sudo mn -c > /dev/null 2>&1 ")
    system("rm -rf ./captures/*.csv")

    controller = RemoteController("c1", ip="127.0.0.1", port=6633)
    topo = CustomTopology()
    net = Mininet(
        topo=topo,
        switch=OVSKernelSwitch,
        build=False,
        controller=controller,
        autoSetMacs=True,
        autoStaticArp=True,
        link=TCLink,
    )

    net.start()
    
    system("ryu-manager simple_switch_13.py > /dev/null 2>&1 &")
    
    print("...Traffic...")
    generate_traffic(net, duration=60)  # Generate traffic for 60 seconds

    # Start packet sniffer threads for each host
    sniffer_tasks = []
    csv_files = []
    
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
        sniffer_task = asyncio.create_task(packet_sniffer(iface, csv_file))
        sniffer_tasks.append(sniffer_task)
        csv_files.append(csv_file)
        
    # Wait for the iperf session to finish
    # await asyncio.sleep(10)  # Adjust the time as needed

    # Wait for the sniffer tasks to finish
    await asyncio.gather(*sniffer_tasks)
            
    # Close CSV files
    for csv_file in csv_files:
        csv_file.close()

    # CLI to inspect the network
    # CLI(net)

    # Clean up
    net.stop()
    print("Clean up.")
    system("sudo mn -c > /dev/null 2>&1 ")
    # system("clear")

if __name__ == '__main__':
    setLogLevel('info')
    asyncio.run(run_topology())