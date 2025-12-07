#!/bin/bash

echo "Starting Disaster Prediction System..."
echo ""

echo "Step 1: Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Step 2: Starting API Server on port 5000..."
gnome-terminal -- bash -c "python api_server.py; exec bash" &

echo ""
echo "Waiting 3 seconds for API server to start..."
sleep 3

echo ""
echo "Step 3: Starting Web Server on port 3000..."
gnome-terminal -- bash -c "python -m http.server 3000; exec bash" &

echo ""
echo "========================================"
echo "Servers are starting!"
echo "========================================"
echo "API Server: http://localhost:5000"
echo "Web Interface: http://localhost:3000"
echo "Heatmaps: http://localhost:3000/heatmaps.html"
echo ""

