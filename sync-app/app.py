#!/usr/bin/env python3

import requests
import json
import logging
import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Configuration of sFlow and InfluxDB URLs
# TODO: Move to an external .ini file
SFLOW_RT_URL = 'http://localhost:8008'
INFLUXDB_URL = 'http://localhost:8086'
INFLUXDB_TOKEN = 'OaujNLMeQcH3ziNdeP-huuOIdiJPgSwh2nR9mDqwF5tlu5kYQ6RO1KzCdr8lBShb_w0vGwxxWoZulLIojIEd3w=='
INFLUXDB_ORG = 'ibn'
INFLUXDB_BUCKET = 'ibn'

# Define the logger Object
logger = logging.getLogger(__name__)

# Configuring flows for RTT and Loss and Jitter
USER_FLOWS = [
        {
            "name": "tcp_rtt",
            "definition": {
                'keys': 'ipsource,ipdestination,tcpsourceport,tcpdestinationport', 
                'value': 'tcprtt',
                'log': True
            
            }
        }, 
        {
            "name": "tcp_lost",
            "definition": {
                'keys': 'ipsource,ipdestination,tcpsourceport,tcpdestinationport', 
                'value': 'tcplost',
                'log': True
            }
        }, 
        {
            "name": "tcp_jitter",
            "definition": {
                'keys':'ipsource,ipdestination,tcpsourceport,tcpdestinationport', 
                'value':'tcprttvar',
            'log':True

            }
        } 
]

# Define the flow in sFlow-RT
def define_flows():
    for flow in USER_FLOWS:
        response = requests.post(f'{SFLOW_RT_URL}/flow/{flow["name"]}/json', data=json.dumps(flow["definition"]))
        if response.status_code == 200:
            print(f"Flow {flow['name']} defined successfully.")
        else:
            print(f"Error defining flow {flow['name']}: {response.status_code} - {response.text}")

    response = requests.post(f'{SFLOW_RT_URL}/flow/flowName/json', data=json.dumps(flow["definition"]))
    if response.status_code in [200, 204]:
        print("Flow defined successfully.")
    else:
        print(f"Error defining flow: {response.status_code} - {response.text}")


# Get metrics from the defined flows
def get_flow_metrics(flow_name):
    url = f'{SFLOW_RT_URL}/metric/{flow_name}/json'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error fetching metrics for {flow_name}: {response.status_code}')
        return None


# Send metrics to InfluxDB
def send_to_influxdb(data, flow_name):
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    for metric in data:
        point = Point("sflow_metrics").tag("flow_name", flow_name)
        for key, value in metric.items():
            if isinstance(value, (int, float)):  # Ensure only numeric values are sent as fields
                point = point.field(key, value)
            else:  # Non-numeric values are sent as tags
                point = point.tag(key, value)
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info('Started')

    define_flows()
    time.sleep(10)  # Wait for some data to be collected

    while True:
        logger.info("Starting the loop")
        flow_names = ["tcp_rtt", "tcp_lost", "tcp_jitter"]
        for flow_name in flow_names:
            metrics = get_flow_metrics(flow_name)
            if metrics:
                print(f"Data for {flow_name} received from sflow-rt.")
                print(metrics)
                # send_to_influxdb(metrics, flow_name)
            else:
                print(f"No data to send for {flow_name}.")
        time.sleep(10)  # Adjust the sleep time as needed