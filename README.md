# Mininet emulation environment for IBN Demo

TODO: Add description of the files here.

# Requirements

 - Docker: Install docker following the [official documentation](https://docs.docker.com/engine/install/ubuntu/)

 - sflow-rt:

 - host sFlow:
```
wget -c https://github.com/sflow/host-sflow/releases/download/v2.0.25-3/hsflowd-ubuntu12_2.0.25-3_amd64.deb
sudo dpkg -i hsflowd-ubuntu12_2.0.25-3_amd64.deb 
```

# Compile host-slow (to export TCP Info fields)

```
apt install libnfnetlink-dev libpcap-dev libdbus-1-dev

cd /demos
git clone https://github.com/sflow/host-sflow.git
cd host-sflow
make FEATURES="NFLOG PCAP OVS TCP DBUS"
sudo make install
sudo chmod +x /usr/sbin/hsflowd

```

# Instructions to run

1. Move to the demo directory:
```
cd /demos/mininet-sflow/
```

2. Make sure the Onos controller and sflow-rt containers are running and Mininet interfaces are cleared
```
sudo docker compose up -d
sudo mn -c
```

3. Run the Mininet script as root (need root privileges to create interfaces)
   - To run the TCLink version:
```
sudo ./host-sflow-tc.py
```
   - To Run the no-TC vesion:
```
sudo ./host-sflow-notc.py
```

4. Once the scipt is initialized, run the `iperf` test (e.g., from h1 to h5 (h5 IP address is 10.0.0.5)
```
containernet> h1 iperf -c 10.0.0.5 -t 30 -i 1
```
> With the `*-notc.py` you will observe a very high datarate between hosts, reaching the magnitude of Gbps 
> because there is not bandwidth limitation for the links

> With the `*-.tc.py` version, even though the selected path is configured with links of maximum data rate of
> 100 Mbps, the iperf test only reaches ~20 Mbps.
