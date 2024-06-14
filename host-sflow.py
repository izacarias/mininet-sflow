#!/usr/bin/env python3

import os
from time import sleep
import requests
import json
from mininet.net import Mininet, CLI
from mininet.node import RemoteController, Host, OVSKernelSwitch
from mininet.log import setLogLevel, info, error
from mininet.link import TCLink, Intf
from requests.auth import HTTPBasicAuth
from configparser import ConfigParser


'''
    Reads external configuration
'''
config = ConfigParser()
config.read("config.ini")
# ONOS Configurations
ONOS_URL = str(config.get("onos", "url"))
ONOS_USER = str(config.get("onos", "user"))
ONOS_PASS = str(config.get("onos", "password"))
ONOS_FLOWS_URL = f"{ONOS_URL}/onos/v1/intents"

'''
    Install rules stored in a json file into Onos Controller
'''
def install_rules_from_file(filename):
    info( '*** Install flow rules from ' + filename )
    credentials = HTTPBasicAuth(ONOS_USER, ONOS_PASS)
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    # Load rules from monflows.json
    rules = []
    with open(filename, 'r') as openfile:
        rules = json.load(openfile)
    for rule in rules:
        response = requests.post(ONOS_FLOWS_URL, data=json.dumps(rule), headers=headers, auth=credentials)
        if response.status_code == 201:
            info( "*** Flow rule installed. key=" + rule["key"] + "\n")
        else:
            error( "*** Got wrong answer from ONOS. Flow rule not installed. key=" + rule["key"] + "\n")


'''
    Deletes virtual interfaces created by mininet 
    to communicate with the host computer
'''
def deleteVeths(interfaces):
    for interface in interfaces:
        os.system( f'ip link delete {interface}' )


'''
    Creates virtual interfaces to allow mininet hosts 
    to talk with the host computer
'''
def createVeths():
    # h1
    os.system( 'ip link add root-h1 type veth peer name h1-root' )
    os.system( 'ip link set root-h1 up' )
    os.system( 'ip addr add 192.168.0.2/24 dev root-h1')
    os.system( 'ip route add 192.168.0.101/32 dev root-h1' )
    # h2
    os.system( 'ip link add root-h2 type veth peer name h2-root' )
    os.system( 'ip link set root-h2 up' )
    os.system( 'ip addr add 192.168.0.2/24 dev root-h2')
    os.system( 'ip route add 192.168.0.102/32 dev root-h2' )
    # h3
    os.system( 'ip link add root-h3 type veth peer name h3-root' )
    os.system( 'ip link set root-h3 up' )
    os.system( 'ip addr add 192.168.0.2/24 dev root-h3')
    os.system( 'ip route add 192.168.0.103/32 dev root-h3' )
    # h4
    os.system( 'ip link add root-h4 type veth peer name h4-root' )
    os.system( 'ip link set root-h4 up' )
    os.system( 'ip addr add 192.168.0.2/24 dev root-h4')
    os.system( 'ip route add 192.168.0.104/32 dev root-h4' )


'''
    Creates and configures the network
'''
def demo_network():
    info( '*** Creating the virtual ethernet pairs to communicate with the host\n' )
    deleteVeths(['root-h1', 'root-h2', 'root-h3', 'root-h4'])
    createVeths()

    info( '*** Creating Mininet network\n')
    net = Mininet( topo=None, build=False, ipBase='10.0.0.0/8', link=TCLink)

    info( '*** Adding remote controller\n')
    c0 = net.addController(name='c0', controller=RemoteController, 
                         ip='localhost',
                         protocol='tcp',
                         port=6653)

    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch, protocols="OpenFlow13")
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch, protocols="OpenFlow13")

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)

    h5 = net.addHost('h5', cls=Host, ip='10.0.0.5', defaultRoute=None)
    h6 = net.addHost('h6', cls=Host, ip='10.0.0.6', defaultRoute=None)
    h7 = net.addHost('h7', cls=Host, ip='10.0.0.7', defaultRoute=None)
    h8 = net.addHost('h8', cls=Host, ip='10.0.0.8', defaultRoute=None)

    info( '*** Connect hosts to s1\n')
    net.addLink(h1, s1, bw=1000)
    net.addLink(h2, s1, bw=1000)
    net.addLink(h3, s1, bw=1000)
    net.addLink(h4, s1, bw=1000)

    info( '*** Connect hosts to s2\n')
    net.addLink(h5, s2, bw=1000)
    net.addLink(h6, s2, bw=1000)
    net.addLink(h7, s2, bw=1000)
    net.addLink(h8, s2, bw=1000)

    info( '*** Add transport links\n')
    net.addLink( s1, s2, bw=100, delay='7ms',   jitter='1ms',  loss=1 )   # Fiber
    net.addLink( s1, s2, bw=250, delay='30ms',  jitter='10ms', loss=4 )   # Satellite
    net.addLink( s1, s2, bw=100, delay='20ms',  jitter='5ms',  loss=2 )   # Satellite II
    net.addLink( s1, s2, bw=50,  delay='10ms',  jitter='2ms',  loss=1 )   # Mobile Connection

    info( '*** Adding interface to root namespace\n')
    _intf_m1 = Intf( 'h1-root', h1)
    _intf_m2 = Intf( 'h2-root', h2)
    _intf_m3 = Intf( 'h3-root', h3)
    _intf_m4 = Intf( 'h4-root', h4)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([c0])
    net.get('s2').start([c0])

    info( '*** Adding IP address to root-namespace interfaces\n' )
    # h1
    h1.cmd( ' ip addr add 192.168.0.101/24 dev h1-root' )
    h1.cmd( ' ip route add 192.168.124.0/24 dev h1-root ' )
    # h2
    h2.cmd( ' ip addr add 192.168.0.102/24 dev h2-root' )
    h2.cmd( ' ip route add 192.168.124.0/24 dev h2-root ' )
    # h3
    h3.cmd( ' ip addr add 192.168.0.103/24 dev h3-root' )
    h3.cmd( ' ip route add 192.168.124.0/24 dev h3-root ' )
    # h4
    h4.cmd( ' ip addr add 192.168.0.104/24 dev h4-root' )
    h4.cmd( ' ip route add 192.168.124.0/24 dev h4-root ' )

    info( '*** Waiting 2 seconds to update topology in ONOS\n')
    sleep(2)
    
    info( '*** Selecting Link 1 for all hosts\n')
    # install_rules_from_file("select-l1.json")

    info( '*** Starting Mininet CLI' )
    CLI(net)
    
'''
    Call the main function
'''
if __name__ == '__main__':
    setLogLevel( 'info' )
    demo_network()