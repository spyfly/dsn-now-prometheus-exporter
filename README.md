# DSN Now Prometheus Exporter

This script retrieves Deep Space Network (DSN) data from a specified URL, processes the XML data, and exports relevant metrics to Prometheus.

## Functions:
- `fetch_data()`: Retrieves XML data from a specified URL using pycurl and returns the decoded data.
- `generate_metrics()`: Processes the retrieved XML data, extracts relevant information, and returns it as a dictionary.
- `parse_data(data)`: Processes the provided data dictionary and sets Prometheus metrics based on the extracted information.
- `main()`: Starts the Prometheus HTTP server, periodically retrieves and processes DSN data, and exports metrics.

## Prometheus Metrics:
- `gauge_azimuth_angle`: Azimuth angle of the dish.
- `gauge_elevation_angle`: Elevation angle of the dish.
- `gauge_wind_speed`: Wind speed at the dish.
- `gauge_signal_power`: Signal power of the communication.
- `gauge_data_rate`: Data rate of the communication.
- `gauge_signal_active`: Signal active status.
- `gauge_upleg_range`: Upleg range to the spacecraft.
- `gauge_downleg_range`: Downleg range from the spacecraft.
- `gauge_rtlt`: Round trip light time (RTLT).

## Prometheus Configuration

- Add the configuration from `prometheus.dsn_exporter.yml`

## Usage:
- Install the Python Dependencies from the `requirements.txt`
- Run the script `./run.sh` to start the Prometheus HTTP server on port 8000 and periodically export DSN metrics.