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

def run_topology():
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
    
    # CLI to inspect the network
    CLI(net)

    # Clean up
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run_topology()