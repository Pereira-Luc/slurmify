#!/bin/bash

# Start the web application in the background
echo "Starting web application..."
python main.py --web > output_web.log 2>&1 &
WEB_PID=$!
echo "Web application started with PID: $WEB_PID. Output is logged to output_web.log"

# Start the API application in the background
echo "Starting API application..."
python main.py --api > output_api.log 2>&1 &
API_PID=$!
echo "API application started with PID: $API_PID. Output is logged to output_api.log"

echo "Both applications are starting in the background."
