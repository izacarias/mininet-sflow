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

Compile host-slow (to export TCP Info fields)

apt install libnfnetlink-dev libpcap-dev libdbus-1-dev

cd /demos
git clone https://github.com/sflow/host-sflow.git
cd host-sflow
make FEATURES="NFLOG PCAP OVS TCP DBUS"
sudo make install
sudo chmod +x /usr/sbin/hsflowd
