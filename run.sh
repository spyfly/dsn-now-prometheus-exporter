#!/bin/bash

# Run exporter.py in a loop
while true; do
  python3 exporter.py
  echo "Exporter crashed, restarting in 5 seconds..."
  sleep 5
done