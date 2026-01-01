# 🚀 Quick Start Guide - GeospatialVR

## Start the Application

### Step 1: Start API Server (Terminal 1)
```powershell
python api_server.py
```

**Expected output:**
```
Starting Disaster Prediction API Server...
API Endpoints:
  GET  /api/predictions - Get disaster predictions
  POST /api/predictions/run - Run predictions with custom parameters
  POST /api/predictions/refresh - Refresh predictions
  GET  /heatmaps.html - View heatmaps
  GET  /disaster_dashboard.html - View disaster dashboard (RECOMMENDED)
 * Running on http://0.0.0.0:5000
```

### Step 2: Start Web Server (Terminal 2)
```powershell
python -m http.server 3000
```

**Expected output:**
```
Serving HTTP on :: port 3000 (http://[::]:3000/) ...
```

## Access the Application

1. **Main VR Application:** http://localhost:3000
2. **Prediction Dashboard:** http://localhost:3000/disaster_dashboard.html
3. **Legacy Heatmaps:** http://localhost:3000/heatmaps.html

## Troubleshooting

### Error: "Cannot connect to API server"

**Check:**
1. Is `python api_server.py` running in Terminal 1?
2. Do you see "Running on http://0.0.0.0:5000" in the output?
3. Try accessing http://localhost:5000/api/pipeline-advantage in your browser
   - Should show JSON data
   - If you get "connection refused", the API server isn't running

**Fix:**
- Restart the API server: `Ctrl+C` then run `python api_server.py` again
- Check if port 5000 is blocked: `netstat -ano | findstr :5000`

### POIs Overlapping in VR

**Recent fix applied:**
- POI positions have been spread out more
- Heights adjusted to reduce overlap
- Warning POIs made taller (height 100) to stand out

**Manual adjustment:** Edit `script/geospatialxr.js` and change:
- `lat` and `lon` values (spread further apart)
- `height` values (make them different heights)

### Dashboard Shows "Data unavailable"

**This means:**
- API server (port 5000) is not responding
- Follow "Error: Cannot connect to API server" steps above

## Features

### Parallel Processing Dashboard
- **Workers:** Control number of CPU cores
- **Chunk Size:** Adjust inference batch size
- **Skip Sequential:** Toggle baseline comparison
- **Show Pipeline:** Display pipeline stages

### Click-to-VR
- Click any state in Flood/Fire panels
- Launches VR with ML-predicted disaster extent
- Flood level scales with probability (0-5m)
- Fire intensity scales with probability (0-10 points)

### Pipeline Advantage
- Shows Sequential vs Pipelined vs Shared execution
- Real speedup calculations
- Performance metrics

## File Structure

```
api_server.py               - Flask API (port 5000)
parallel_disaster_prediction.py - ML model with parallelism
pipeline_simulator.py       - Pipeline advantage simulation
disaster_dashboard.html     - Interactive dashboard
index.html                  - Main VR application
script/geospatialxr.js     - VR controls & state mapping
```

## Dependencies

Install if missing:
```powershell
pip install pandas numpy scikit-learn flask flask-cors
```
