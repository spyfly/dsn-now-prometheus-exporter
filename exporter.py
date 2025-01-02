import time
import xml.etree.ElementTree as ET
import urllib.request
import json
import pycurl
import certifi
from io import BytesIO
from prometheus_client import start_http_server, Gauge

def fetch_data():
    # Use pycurl instead of urllib

    # Set the URL for the XML data
    url = "https://eyes.nasa.gov/dsn/data/dsn.xml" # Replace this with the actual URL

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.CAINFO, certifi.where())
    c.perform()
    c.close()

    body = buffer.getvalue()
    decoded = body.decode('utf-8')

    return decoded

def generate_metrics():
    xml_data = fetch_data()
    root = ET.fromstring(xml_data)

    # Accessing elements using their XPath expression
    dsnObj = []
    timestamp = 0
    rootEls = root.findall('*')
    station = -1
    dish = -1
    for rootEl in rootEls:
        prefix = " "
        if (rootEl.tag == "station"):
            dish = -1
            station += 1
            stationObj = rootEl.attrib
            stationObj["dishes"] = []
            dsnObj.append(stationObj)
            prefix = ""
            print("------------------------------------------------------------------------------")
        if (rootEl.tag == "dish"):
            dishObj = rootEl.attrib
            dishObj["comms"] = []
            dsnObj[station]["dishes"].append(dishObj)
            dish += 1
        if (rootEl.tag == "timestamp"):
            print("Timestamp:", rootEl.text)
            timestamp = rootEl.text
        print(prefix + rootEl.tag, rootEl.attrib)
        subElements = rootEl.findall("*")
        for subElement in subElements:
            print(">", subElement.tag, subElement.attrib)
            subObj = subElement.attrib
            subObj["type"] = subElement.tag
            dsnObj[station]["dishes"][dish]["comms"].append(subObj)

        #signals = dish.findall('downSignal')
        #for signal in signals:
        #    print("\tTarget name:", signal.get('spacecraft'))
        #    print("\tData rate:", signal.get('dataRate'))
        #    print("\tFrequency:", signal.get('frequency'))
        #    print("\tBand:", signal.get('band'))
        #    print("\tPower:", signal.get('power'))
        #    print()
        #print(json.dumps(dsnObj, indent=4))
        # Export the data to a file
    #with open('dsn.json', 'w') as f:
    #    json.dump(dsnObj, f, indent=4)

        # Send metrics from dsn.json to Prometheus
    return {"stations": dsnObj, "timestamp": timestamp}

from prometheus_client import start_http_server, Gauge
import time
import json

# Define Prometheus metrics for different categories

# Dish-related metrics
gauge_azimuth_angle = Gauge('dish_azimuth_angle', 'Azimuth angle of the dish', ['station', 'dish', 'timestamp'])
gauge_elevation_angle = Gauge('dish_elevation_angle', 'Elevation angle of the dish', ['station', 'dish', 'timestamp'])
gauge_wind_speed = Gauge('dish_wind_speed', 'Wind speed at the dish', ['station', 'dish', 'timestamp'])

# Signal-related metrics (up and down signals)
gauge_signal_power = Gauge('signal_power', 'Signal power of the communication', ['station', 'dish', 'spacecraft', 'signal_type', 'band', 'direction', 'timestamp'])
gauge_data_rate = Gauge('signal_data_rate', 'Data rate of the communication', ['station', 'dish', 'spacecraft', 'signal_type', 'band', 'direction', 'timestamp'])
gauge_signal_active = Gauge('signal_active_status', 'Signal active status', ['station', 'dish', 'spacecraft', 'signal_type', 'direction', 'timestamp'])

# Target-related metrics (tracking data)
gauge_upleg_range = Gauge('target_upleg_range', 'Upleg range to the spacecraft', ['station', 'dish', 'spacecraft', 'timestamp'])
gauge_downleg_range = Gauge('target_downleg_range', 'Downleg range from the spacecraft', ['station', 'dish', 'spacecraft', 'timestamp'])
gauge_rtlt = Gauge('target_rtlt', 'Round trip light time (RTLT)', ['station', 'dish', 'spacecraft', 'timestamp'])

# Data from the user
data = [
    # Your dataset here
]

def parse_data(data):
    stations = data['stations']
    timestamp = int(data['timestamp'])
    for station in stations:
        station_name = station['friendlyName']

        for dish in station['dishes']:
            dish_name = dish['name']

            # Parse dish-related metrics
            #azimuth_angle = float(dish['azimuthAngle'])
            #elevation_angle = float(dish['elevationAngle'])
            #wind_speed = float(dish['windSpeed'])

            # Set Prometheus metrics for the dish with the timestamp label
            #gauge_azimuth_angle.labels(station=station_name, dish=dish_name, timestamp=timestamp).set(azimuth_angle)
            #gauge_elevation_angle.labels(station=station_name, dish=dish_name, timestamp=timestamp).set(elevation_angle)
            #gauge_wind_speed.labels(station=station_name, dish=dish_name, timestamp=timestamp).set(wind_speed)

            # Parse communication metrics
            for comm in dish['comms']:
                spacecraft = comm.get('spacecraft', 'unknown')
                name = comm.get('name', 'unknown')
                comm_type = comm['type']

                # Handle signal metrics
                if comm_type in ['upSignal', 'downSignal']:
                    direction = 'uplink' if comm_type == 'upSignal' else 'downlink'
                    band = comm['band']
                    signal_type = comm.get('signalType', 'unknown')

                    # Signal power
                    if comm.get('power'):
                        power = float(comm['power'])
                        gauge_signal_power.labels(station=station_name, dish=dish_name, spacecraft=spacecraft, signal_type=signal_type, band=band, direction=direction, timestamp=timestamp).set(power)
                    
                    # Signal data rate
                    if comm.get('dataRate'):
                        data_rate = float(comm['dataRate'])
                        gauge_data_rate.labels(station=station_name, dish=dish_name, spacecraft=spacecraft, signal_type=signal_type, band=band, direction=direction, timestamp=timestamp).set(data_rate)
                    
                    # Signal active status
                    if comm.get('active'):
                        active = 1 if comm['active'] == "true" else 0
                        gauge_signal_active.labels(station=station_name, dish=dish_name, spacecraft=spacecraft, signal_type=signal_type, direction=direction, timestamp=timestamp).set(active)

                # Handle target metrics
                if comm_type == 'target':
                    if comm.get('uplegRange'):
                        upleg_range = float(comm['uplegRange'])
                        gauge_upleg_range.labels(station=station_name, dish=dish_name, spacecraft=name, timestamp=timestamp).set(upleg_range)

                    if comm.get('downlegRange'):
                        downleg_range = float(comm['downlegRange'])
                        gauge_downleg_range.labels(station=station_name, dish=dish_name, spacecraft=name, timestamp=timestamp).set(downleg_range)

                    if comm.get('rtlt'):
                        rtlt = float(comm['rtlt'])
                        gauge_rtlt.labels(station=station_name, dish=dish_name, spacecraft=name, timestamp=timestamp).set(rtlt)

def main():
    # Start the Prometheus HTTP server on port 8000
    start_http_server(8000, '127.0.0.1')

    # Parse the dataset and export metrics
    while True:
        data = generate_metrics()
        parse_data(data)
        time.sleep(5)  # Refresh the metrics every 15 seconds

if __name__ == '__main__':
    main()
