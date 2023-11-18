from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import irange,dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import RemoteController

import argparse
import sys
import time


class FatTreeTopo(Topo):

    def __init__(self, pods, **kwargs):
        # Initialize topology and default options
        Topo.__init__(self, **kwargs)
        c0 = RemoteController ('c0','127.0.0.1', port=6633)
        hosts = []
        aggrs = []
        edges = []
        cores = []

        for c in range (0, int(pods**2/4)):
            cores.append(self.addSwitch('c' + str((len(cores) + 1))))
        for p in range (0,pods):
            for a in range (0, int(pods/2)):
                aggrs.append(self.addSwitch('a' + str((len(cores) + len(aggrs) + 1))))

        # Create edge switches
        for p in range (0,pods):
            for e in range (0, int(pods/2)):
                edges.append(self.addSwitch('e' + str((len(cores) + len(aggrs) + len(edges) + 1))))
        
        # Create hosts
        for edge in edges:
            for h in range (0, int(pods/2)):
                host = self.addHost('h' + str((len(hosts) + 1)))
                hosts.append(host)
                self.addLink(edge, host)

        # Create links between aggregate and core switches
        l = 0
        for podNumber in range (0,pods):
            for aggr in range (0, int(pods/2)):
                for port in range (0, int(pods/2)):
                    if aggr == 0 and port == 0:
                        l = podNumber
                    else:
                        l = (l + 1) % (int(pods**2/4))
                    self.addLink(aggrs [podNumber * int(pods/2) + aggr], cores [l])   

        # Create links between aggregate and edge switches
        for podNumber in range (0,pods):
            for aggr in range (0, int(pods/2)):
                for edge in range (0, int(pods/2)):
                    self.addLink(aggrs [podNumber * int(pods/2) + aggr], edges [podNumber * int(pods/2) + edge])         

        


def setup_fattree_topology(pods=4):
    assert(pods>0)
    assert((pods % 2) == 0)
    topo = FatTreeTopo(pods)
    net = Mininet(topo=topo, autoSetMacs=True, link=TCLink)
    net.start()
    time.sleep(5) #wait 5 sec for routing to converge
    net.pingAll()  #test all to all ping and learn the ARP info over this process
    # print(net.links)
    CLI(net)     
    net.stop()  

topos = { 'fattreetopo': ( lambda: FatTreeTopo(pods=4) ) }


    
def main(argv):
    parser = argparse.ArgumentParser(description="Parse input information for mininet Fat-Tree network")
    parser.add_argument('--pod_numbers', '-k', dest='pods', type=int, help='pod numbers')
    args = parser.parse_args(argv)
    setLogLevel('info')
    setup_fattree_topology(args.pods)


if __name__ == '__main__':
    main(sys.argv[1:])
