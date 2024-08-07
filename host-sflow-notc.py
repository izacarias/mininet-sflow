#!/usr/bin/env python3

import os
from time import sleep
import requests
import json
from mininet.net import Mininet, CLI
from mininet.node import RemoteController, Host, OVSKernelSwitch, Controller
from mininet.log import setLogLevel, info, error
from mininet.link import Link, TCLink, TCULink, Intf
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
# Host network address
HOST_NETWORK = str(config.get("host", "network"))

'''
    Install rules stored in a json file into Onos Controller
'''
def install_flows_from_file(file_name):
    info( '*** Installing flows from ' + file_name + "\n")
    ONOS_FLOWS_URL = f"{ONOS_URL}/onos/v1/flows?appId=org.onosproject.ibn"
    credentials = HTTPBasicAuth(ONOS_USER, ONOS_PASS)
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    # Load flows from file_name
    flows = []
    with open(file_name, 'r') as openfile:
        set_of_flows = json.load(openfile)
    for obj_flow in set_of_flows:
        data = json.dumps(obj_flow)
        # info( "*** Installing flow " + data + "\n")
        response = requests.post(
            ONOS_FLOWS_URL, 
            data=data, 
            headers=headers, 
            auth=credentials
        )
        if response.status_code in [200, 201]:
            # set_of_flows[0]["flows"][0]["id"]
            for flow in obj_flow["flows"]:
                info( f'*** Flow rule installed. key={flow["id"]}\n')
        else:
            for flow in obj_flow["flows"]:
                err_code = response.json()["code"]
                err_msg = response.json()["message"]
                error( "*** Got wrong answer from ONOS. Flow rule not installed. key=" + flow["id"] + "\n")
                error( "*** The error was: " + err_msg + "\n")


'''
    Delete all rules installed by this script
'''
def delete_installed_rules(application_name="org.onosproject.ibn"):
    info( '*** Deleting rules installed by the script\n')
    ONOS_DELETE_URL = f"{ONOS_URL}/onos/v1/flows/application/{application_name}"
    credentials = HTTPBasicAuth(ONOS_USER, ONOS_PASS)
    headers = {"Accept": "application/json"}
    response = requests.delete(
        ONOS_DELETE_URL,
        headers=headers,
        auth=credentials
    )
    if response.status_code in [204]:
        info( '*** All flows openflow flows deleted from the controller \n')
    else:
        err_code = response.json()["code"]
        err_msg = response.json()["message"]
        info( f'*** Error deleting flows from the ONOS controller. Code = {err_code} with Message = {err_msg}\n')


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
    info( '*** Deleting old virtual ethernet pairs\n' )
    deleteVeths(['root-h1', 'root-h2', 'root-h3', 'root-h4'])
    info( '*** Creating the virtual ethernet pairs to communicate with the host\n' )
    createVeths()

    info( '*** Creating Mininet network\n')
    net = Mininet( topo=None, build=False, ipBase='10.0.0.0/8', link=Link, autoStaticArp=True)

    info( '*** Adding remote controller\n')
    c0 = net.addController(name='c0', controller=RemoteController, 
                        ip='localhost',
                        protocol='tcp',
                        port=6653)

    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch, protocols="OpenFlow13")
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch, protocols="OpenFlow13")

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', mac='8e:e1:03:00:00:01', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', mac='8e:e1:03:00:00:02', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', mac='8e:e1:03:00:00:03', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4', mac='8e:e1:03:00:00:04', defaultRoute=None)

    h5 = net.addHost('h5', cls=Host, ip='10.0.0.5', mac='8e:e1:03:00:00:05', defaultRoute=None)
    h6 = net.addHost('h6', cls=Host, ip='10.0.0.6', mac='8e:e1:03:00:00:06', defaultRoute=None)
    h7 = net.addHost('h7', cls=Host, ip='10.0.0.7', mac='8e:e1:03:00:00:07', defaultRoute=None)
    h8 = net.addHost('h8', cls=Host, ip='10.0.0.8', mac='8e:e1:03:00:00:08', defaultRoute=None)

    info( '*** Connect hosts to s1\n')
    net.addLink(h1, s1, cls=Link)
    net.addLink(h2, s1, cls=Link)
    net.addLink(h3, s1, cls=Link)
    net.addLink(h4, s1, cls=Link)

    info( '*** Connect hosts to s2\n')
    net.addLink(h5, s2, cls=Link)
    net.addLink(h6, s2, cls=Link)
    net.addLink(h7, s2, cls=Link)
    net.addLink(h8, s2, cls=Link)

    info( '*** Add transport links\n')
    net.addLink( s1, s2, bw=100, delay='5ms', jitter='1ms', loss=1)   # Fiber
    net.addLink( s1, s2, bw=250, delay='5ms', jitter='1ms', loss=4)   # Satellite
    net.addLink( s1, s2, bw=100, delay='5ms', jitter='1ms', loss=2)   # Satellite II
    net.addLink( s1, s2, bw=50,  delay='5ms', jitter='1ms', loss=1)   # Mobile Connection

    info( '*** Adding interface to root namespace\n')
    _intf_m1 = Intf( 'h1-root', h1)
    _intf_m2 = Intf( 'h2-root', h2)
    _intf_m3 = Intf( 'h3-root', h3)
    _intf_m4 = Intf( 'h4-root', h4)

    info( '*** Starting network\n' )
    net.build()
    info( '*** Starting controllers\n' )
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n' )
    net.get( 's1' ).start( [c0] )
    net.get( 's2' ).start( [c0] )

    info( '*** Adding IP address to root-namespace interfaces\n' )
    # h1
    h1.cmd( ' ip addr add 192.168.0.101/24 dev h1-root' )
    h1.cmd( ' ip route add ' + HOST_NETWORK + ' dev h1-root ' )
    # h2
    h2.cmd( ' ip addr add 192.168.0.102/24 dev h2-root' )
    h2.cmd( ' ip route add ' + HOST_NETWORK + ' dev h2-root ' )
    # h3
    h3.cmd( ' ip addr add 192.168.0.103/24 dev h3-root' )
    h3.cmd( ' ip route add ' + HOST_NETWORK + ' dev h3-root ' )
    # h4
    h4.cmd( ' ip addr add 192.168.0.104/24 dev h4-root' )
    h4.cmd( ' ip route add ' + HOST_NETWORK + ' dev h4-root ' )

    info( '*** Waiting 2 seconds to update topology in ONOS\n')
    sleep(2)
    
    info( '*** Installing ARP rules\n')
    # install_flows_from_file( "of-arp.json" )
    
    info( '*** Installing IPv4 rules\n')
    install_flows_from_file( "of-ip.json" )
    
    info( '*** Selecting Path1 for all hosts\n' )
    install_flows_from_file( "of-select-p1.json" )

    info( '*** Running hsflow process in h1 ... h4 \n')
    h1.cmd( ' hsflowd -f /demos/mininet-sflow/hsflow/h1.conf -p /demos/mininet-sflow/hsflow/hsflow/h1.pid ' )
    h2.cmd( ' hsflowd -f /demos/mininet-sflow/hsflow/h2.conf -p /demos/mininet-sflow/hsflow/hsflow/h2.pid ' )
    h3.cmd( ' hsflowd -f /demos/mininet-sflow/hsflow/h3.conf -p /demos/mininet-sflow/hsflow/hsflow/h3.pid ' )
    h4.cmd( ' hsflowd -f /demos/mininet-sflow/hsflow/h4.conf -p /demos/mininet-sflow/hsflow/hsflow/h4.pid ' )

    h1.cmd( 'iptables -I INPUT -j NFLOG -m statistic --mode random --probability 0.0025 --nflog-group 5 --nflog-prefix SFLOW'  )
    h1.cmd( 'iptables -I OUTPUT -j NFLOG -m statistic --mode random --probability 0.0025 --nflog-group 5 --nflog-prefix SFLOW' )
    h2.cmd( 'iptables -I INPUT -j NFLOG -m statistic --mode random --probability 0.0025 --nflog-group 5 --nflog-prefix SFLOW'  )
    h2.cmd( 'iptables -I OUTPUT -j NFLOG -m statistic --mode random --probability 0.0025 --nflog-group 5 --nflog-prefix SFLOW' )
    h3.cmd( 'iptables -I INPUT -j NFLOG -m statistic --mode random --probability 0.0025 --nflog-group 5 --nflog-prefix SFLOW'  )
    h3.cmd( 'iptables -I INPUT -j NFLOG -m statistic --mode random --probability 0.0025 --nflog-group 5 --nflog-prefix SFLOW'  )
    h4.cmd( 'iptables -I OUTPUT -j NFLOG -m statistic --mode random --probability 0.0025 --nflog-group 5 --nflog-prefix SFLOW' )
    h4.cmd( 'iptables -I OUTPUT -j NFLOG -m statistic --mode random --probability 0.0025 --nflog-group 5 --nflog-prefix SFLOW' )
    
    info( '*** Running iperf process in h5 \n')
    h5.cmd(' iperf -s &')

    info( '*** Starting Mininet CLI \n' )
    CLI(net)

    info( '*** Killing hsflowd agents')
    os.system( ' killall hsflowd ' )

    info( '*** Stopping network\n' )
    delete_installed_rules()
    net.stop()
    
    
'''
    Call the main function
'''
if __name__ == '__main__':
    setLogLevel( 'info' )
    demo_network()
