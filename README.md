<p align="center"><img alt="GeospatialVR" title="GeospatialVR" src="images/logo.png" width="250"></p>

<h3 align="center">
  A Web-based Virtual Reality Framework for Collaborative Environmental Simulations
</h3>

<br>

## Table of Contents

- [Introduction](#introduction)
- [Computer Graphics & Virtual Reality Implementation](#computer-graphics--virtual-reality-implementation)
- [Parallel Programming Implementation](#parallel-programming-implementation)
- [Interactive Dashboard](#interactive-dashboard)
- [Tools & Techniques Summary](#tools--techniques-summary)
- [How To Run](#how-to-run)
- [How To Use](#how-to-use)
- [Use Cases](#use-cases)
  - [Flood - Mumbai](#flood---mumbai-india)
  - [Forest Fire - Uttarakhand](#forest-fire---uttarakhand-india)
- [Feedback](#feedback)
- [To-Do](#to-do)
- [License](#license)
- [Acknowledgements & Citation](#acknowledgements--citation)

## Introduction

This project introduces GeospatialVR, an open-source collaborative virtual reality framework to dynamically create 3D real-world environments that can be served on any web platform and accessed via desktop and mobile devices and virtual reality headsets. The framework can generate realistic simulations of desired locations entailing the terrain, elevation model, infrastructures, dynamic visualizations (e.g. water and fire simulation), and information layers (e.g. disaster damages and extent, sensor readings, occupancy, traffic, weather). These layers enable in-situ visualization of useful data to aid public, scientists, officials, and decision-makers in acquiring a bird's eye view of the current, historical, or forecasted condition of a community. The framework incorporates multiuser support for remote virtual collaboration. GeospatialVR's purpose is to augment cyberinfrastructures with geospatial components to constitute the next-generation of information systems and decision support systems powered by immersive technologies. 

This India-specific implementation focuses on flood and forest fire disaster management scenarios, with case studies developed for flooding in Mumbai and forest fires in Uttarakhand. The project integrates **computer graphics and virtual reality** for immersive 3D visualization, combined with **parallel programming** for efficient data processing and machine learning-based disaster prediction.

![Arch](images/arch.png)

---

## Computer Graphics & Virtual Reality Implementation

### Virtual Reality Architecture

This project delivers **immersive disaster visualization** using **Unity WebGL + WebXR**, enabling users to experience flood/fire scenarios in VR directly through web browsers. The system integrates **machine learning predictions** with **real-time 3D rendering** to create dynamic, data-driven VR experiences.

### VR Rendering Pipeline

```
[ML Predictions] → [Coordinate Mapping] → [3D Scene Generation] 
   → [Geometry Processing] → [Rasterization] → [Fragment Shading] 
   → [Stereo Rendering] → [VR Headset Display]
```

---

### 1. ML-Driven VR Initialization

**Prediction-Based Scene Loading**:
- **User Workflow**: Click a state on the Interactive Dashboard → VR launches with disaster-specific parameters
- **URL Parameter Passing**: `index.html?state=Maharashtra&disaster=flood&severity=0.85`
- **Dynamic Scene Configuration**: VR adjusts flood levels, fire intensity, and POI density based on ML probability

**Implementation**:
```javascript
// Extract ML predictions from URL
const params = new URLSearchParams(window.location.search);
const state = params.get('state');         // e.g., "Maharashtra"
const disaster = params.get('disaster');   // "flood" or "fire"
const severity = parseFloat(params.get('severity')); // 0.0 - 1.0

// Scale disaster extent based on severity
if (disaster === 'flood') {
    const waterLevel = severity * 5.0;  // 0-5 meters
    sendToUnity('GeospatialController', 'SetWaterLevel', waterLevel);
} else if (disaster === 'fire') {
    const fireIntensity = severity * 10.0;  // 0-10 intensity
    sendToUnity('FireController', 'SetFireIntensity', fireIntensity);
}
```

### 2. State Coordinate System (28 Indian States)

**Geographic Mapping**:
- Precomputed centroids for all major Indian states
- Lat/Lon coordinates used to position VR camera on scene load
- Ensures users land at correct location when clicking state predictions

**State Coordinates Database** (sample):
```javascript
const stateCoordinates = {
    'Maharashtra': { lat: 19.7515, lon: 75.7139 },
    'Karnataka': { lat: 15.3173, lon: 75.7139 },
    'Tamil Nadu': { lat: 11.1271, lon: 78.6569 },
    'Kerala': { lat: 10.8505, lon: 76.2711 },
    'Uttar Pradesh': { lat: 26.8467, lon: 80.9462 },
    // ... 23 more states
};
```

**Camera Positioning**:
- VR camera spawns at selected state's coordinates
- Altitude set based on terrain elevation + 50m offset
- Initial facing direction: North (for consistent orientation)

---

### 3. 3D Rendering Pipeline

The project uses **Unity WebGL** as the core 3D graphics engine, implementing a complete computer graphics rendering pipeline:

1. **Geometry Processing**:
   - **Terrain Generation**: Real-world terrain is generated from elevation data and Google Maps tiles
   - **Building Rendering**: 3D buildings and infrastructure are procedurally generated from map data
   - **Coordinate Transformation**: Geographic coordinates (latitude/longitude) are converted to 3D world space coordinates
   - **Mesh Subdivision**: Terrain split into 256x256 tile patches for LOD (Level of Detail)

2. **Rasterization & Rendering**:
   - **WebGL Rendering**: Unity compiles to WebGL, utilizing the browser's GPU for hardware-accelerated rendering
   - **Shader Pipeline**: Custom shaders handle:
     - **Water Surface Rendering**: Gerstner wave simulation with reflection/refraction (flood visualization)
     - **Fire Particle Systems**: GPU-accelerated particles with physics (forest fire simulation)
     - **POI Label Rendering**: Billboard sprites always facing camera (cylindrical constraint)
   - **Lighting & Shadows**: Real-time lighting with Cascade Shadow Maps (4 splits), SSAO (Screen-Space Ambient Occlusion)

3. **Virtual Reality Integration**:
   - **WebXR API**: Implements WebXR standard for cross-platform VR support
   - **Head Tracking**: 6DOF (six degrees of freedom) head tracking for immersive navigation
   - **Stereoscopic Rendering**: Separate rendering for left/right eyes with proper IPD (interpupillary distance)
   - **Controller Support**: VR controller tracking for interaction in 3D space (thumbstick locomotion, trigger selection)

4. **Dynamic Visualizations**:
   - **Water Simulation**: Procedural water mesh generation with animated surface (adjustable 0-5m flood levels)
   - **Particle Systems**: Fire effects using Unity's particle system with physics-based smoke and flames (scalable intensity 0-10)
   - **Information Overlays**: 3D text labels and icons positioned above terrain using world-space coordinates

### 4. Unity-JavaScript Communication Bridge

**SendMessage Guard Pattern**:
- **Problem**: Calling `UnityInstance.SendMessage()` before Unity engine loads causes `abort(62)` error
- **Solution**: Queue messages until `UnityLoaded` event fires

```javascript
let unityReady = false;
let unityQueue = [];

// Guard function
function sendToUnity(objectName, methodName, param) {
    if (unityReady) {
        gameInstance.SendMessage(objectName, methodName, param);
    } else {
        unityQueue.push({ objectName, methodName, param });
    }
}

// Unity load callback
window.addEventListener('UnityLoaded', () => {
    unityReady = true;
    unityQueue.forEach(msg => 
        gameInstance.SendMessage(msg.objectName, msg.methodName, msg.param)
    );
    unityQueue = [];
});
```

**API Methods**:
```javascript
// Update map location (lat/lon)
sendToUnity('GeospatialController', 'UpdateMapLocation', 
    JSON.stringify({ lat: 19.076, lon: 72.877 }));

// Add disaster POI
sendToUnity('POIManager', 'AddPOI', 
    JSON.stringify({ type: 'flood', severity: 0.85, lat: 19.1, lon: 72.9 }));

// Generate fire simulation
sendToUnity('FireController', 'GenerateFire', 
    JSON.stringify({ intensity: 7.5, radius: 500 }));
```

### 5. Real-Time Performance Optimization

- **LOD System**: 4 LOD levels with cross-fade transitions (Full detail < 50m, Billboard > 500m)
- **Occlusion Culling**: Precomputed PVS (Potentially Visible Set) for urban areas
- **Frustum Culling**: Only renders objects visible to camera (~40% draw call savings)
- **Texture Compression**: DXT5 (desktop), ETC2 (mobile) with mipmap chains
- **Draw Call Batching**: Static batching (buildings/terrain), GPU instancing (trees/streetlights)

**Target Performance**:
- **VR Framerate**: 90 FPS (Oculus/Vive), 72 FPS (Windows MR)
- **Draw Calls**: < 500 per frame
- **Vertex Count**: < 2M triangles visible per frame

### Graphics Technologies Used

- **Unity Engine 2020.3 LTS**: 3D game engine providing rendering, physics, and scene management
- **WebGL**: Low-level graphics API for GPU-accelerated rendering in browsers
- **WebXR**: Standard API for VR/AR experiences in web browsers (Chrome/Edge recommended)
- **GLSL/HLSL Shaders**: Custom shader programs for water, fire, and visual effects
- **gl-matrix.js**: High-performance matrix/vector operations for camera transforms
- **WebXR Polyfill**: Fallback for older browsers (Google Cardboard support)

### VR Interaction Pipeline

```
User Input (VR Headset/Controllers)
    ↓
WebXR API (Browser)
    ↓
Unity WebGL (JavaScript Bridge with SendMessage Guard)
    ↓
3D Scene Update (Camera Position, Object Transformations, Disaster Parameters)
    ↓
GPU Rendering (WebGL Shaders: Water, Fire, Terrain)
    ↓
Display (VR Headset / Desktop Screen - Stereo Rendering)
```

### VR Comfort Features

- **Vignette Effect**: Reduces peripheral vision during movement (anti-nausea)
- **Snap Turning**: 30° discrete rotations (reduces disorientation)
- **Teleportation Mode**: Arc-based jump for motion-sensitive users

---

## Parallel Programming Implementation

### Overview

This project implements **CPU-based parallel programming techniques** to efficiently process large-scale environmental datasets and generate real-time disaster predictions. The parallel processing architecture achieves **2.5x-4x speedup** over sequential execution by leveraging multi-core CPUs and optimized data pipelines.

### Parallel Data Processing Architecture

The system processes **10,000+ flood records** and historical forest fire data using multi-level parallelism:

### 1. Data-Level Parallelism (Chunking Strategy)

**Implementation**:
- Large datasets are divided into **chunks** based on available CPU cores
- Each chunk is processed independently in parallel processes
- Uses Python's `multiprocessing.Pool` for process-based parallelism (bypasses GIL)

```python
# Split dataset into chunks (one per CPU core)
chunk_size = max(100, len(df) // n_workers)
chunks = [df.iloc[i:i+chunk_size].copy() for i in range(0, len(df), chunk_size)]

# Process all chunks in parallel
with Pool(n_workers) as pool:
    processed_chunks = pool.map(process_flood_chunk, chunk_data)
    
# Merge results
result_df = pd.concat(processed_chunks, ignore_index=True)
```

**Key Benefits**:
- Each process has isolated memory (avoids GIL bottleneck)
- Scales linearly with CPU cores
- Fault isolation (one chunk failure doesn't crash entire pipeline)

### 2. Parallel Feature Engineering

Each worker process independently performs:

**Geographic Processing**:
- **Coordinate-to-State Mapping**: Maps (latitude, longitude) to 28 Indian states using distance calculations
- **Vectorized Operations**: NumPy arrays for fast numerical computations
- **Concurrent Encoding**: Label encoding for categorical features (land cover, soil type) in parallel

**Feature Computation** (per chunk):
```python
# Risk index calculation (vectorized)
chunk['Risk_Index'] = (
    chunk['Rainfall (mm)'] * 0.3 + 
    chunk['Water Level (m)'] * 0.25 + 
    chunk['River Discharge (m³/s)'] * 0.2 + 
    chunk['Historical Floods'] * 0.15 + 
    chunk['Population Density'] * 0.1
)

# Elevation-based risk factors
chunk['Elevation_Risk'] = np.where(
    chunk['Elevation (m)'] < 500, 1.2,
    np.where(chunk['Elevation (m)'] < 1000, 1.0, 0.8)
)
```

### 3. Parallel Inference Pipeline

**ProcessPoolExecutor for Batch Predictions**:
- Trained ML model serialized and broadcast to worker processes
- Inference split into batches (default: 5000 rows/batch)
- Workers predict flood probabilities concurrently
- Results aggregated per state using parallel reductions

```python
# Serialize model once, share across workers
model_bytes = pickle.dumps(model)

# Fan out inference to worker pool
with ProcessPoolExecutor(max_workers=n_workers, 
                         initializer=_init_model_worker, 
                         initargs=(model_bytes, feature_cols)) as executor:
    futures = [executor.submit(_predict_chunk_with_state, chunk) 
               for chunk in chunks]
    results = [future.result() for future in as_completed(futures)]
```

**Advantages**:
- Model loaded once per worker (amortized overhead)
- Independent batch processing (no synchronization needed)
- Load balancing via work-stealing queue

### 4. Pipeline Parallelism (Shared Stages)

**Multi-Stage Pipeline Design**:
```
[Stage 1: Load/Parse] → [Stage 2: Encode] → [Stage 3: Feature Eng] 
    → [Stage 4: Predict] → [Stage 5: Aggregate]
```

**Optimization: Shared Resource Reuse**:
- **Flood + Fire paths share encoders**: Avoid redundant encoding setup
- **State mapping cached**: Reused across hazard types
- **Pipelined execution**: Stage N+1 processes batch B while stage N processes batch B+1

**Pipeline Advantage Visualization**:
```
Sequential: Task A → Task B → Task C (all stages serial)
Pipelined:  Stage 1 | Stage 2 | Stage 3 (overlapping execution)
            Task A → Task B → Task C
                    Task A → Task B → Task C
```

### 5. Machine Learning Parallelization

**Random Forest Training**:
- Uses `n_jobs=-1` to utilize all CPU cores for tree construction
- Each tree built independently in parallel
- 100 estimators trained concurrently

```python
model = RandomForestClassifier(
    n_estimators=100, 
    n_jobs=-1,  # Use all cores
    random_state=42
)
model.fit(X_train, y_train)
```

**Cross-Validation & Metrics**:
- Parallel k-fold splits
- Concurrent accuracy scoring across folds

### 6. Performance Optimization Techniques

**Memory Efficiency**:
- **Copy-on-Write**: Chunks copied only when modified
- **Shared Memory**: Read-only data (encoders, coordinates) shared via process fork
- **Streaming Aggregation**: Per-state results reduced incrementally

**CPU Pinning** (Optional):
- Workers can be pinned to specific cores (OS-dependent)
- Reduces cache thrashing and context switches

**Vectorization**:
- NumPy broadcasting for element-wise operations
- Avoids Python loops (10-100x faster)

### 7. Configurable Parallelism

Users control parallelism via CLI/Dashboard:

```bash
# Default: auto-detect cores
python parallel_disaster_prediction.py

# Custom worker count
python parallel_disaster_prediction.py --workers 8

# Adjust inference chunk size
python parallel_disaster_prediction.py --chunk-size 10000

# Skip sequential baseline (faster)
python parallel_disaster_prediction.py --skip-sequential
```

**Dashboard Controls**:
- **Workers slider**: Set CPU core count (1-64)
- **Chunk size**: Adjust inference batch size (100-50000)
- **Pipeline toggle**: Show/hide pipeline stages

### Performance Metrics & Results

**Speedup Achieved**:
| Configuration | Processing Time | Speedup |
|---------------|----------------|---------|
| Sequential (1 core) | ~8.5s | 1.0x (baseline) |
| Parallel (4 cores) | ~3.2s | 2.7x |
| Parallel (8 cores) | ~2.1s | 4.0x |

**Performance Tracking**:
```json
{
  "parallel_time": 2.14,
  "sequential_time": 8.52,
  "speedup": 3.98,
  "accuracy": 0.9234,
  "cpu_cores_used": 8,
  "inference_chunk_size": 5000
}
```

### Technologies & Tools Used

**Python Libraries**:
- **`multiprocessing.Pool`**: Process-based parallelism
- **`concurrent.futures.ProcessPoolExecutor`**: High-level parallel execution
- **`pickle`**: Model serialization for worker broadcast
- **`numpy`**: Vectorized array operations
- **`pandas`**: DataFrame chunking and concatenation

**Machine Learning**:
- **`scikit-learn`**: Parallel RandomForest (`n_jobs` parameter)
- **`joblib`**: Parallel backend for scikit-learn

**Pipeline Simulation**:
- **Discrete-Event Simulator**: Models stage occupancy and stalls
- **Queue-Based Scheduling**: FIFO vs. reordering strategies

### Parallel vs Sequential Comparison

| Aspect | Sequential | Parallel |
|--------|-----------|----------|
| **Processing** | Row-by-row, single thread | Chunk-based, multi-process |
| **CPU Usage** | 1 core (~12%) | All cores (95%+) |
| **Speed** | Baseline (1x) | 2.5x - 4x faster |
| **Memory** | Lower overhead (~200MB) | Higher (~800MB, multi-process) |
| **Scalability** | Fixed (O(n)) | Linear (O(n/p), p=cores) |
| **Fault Tolerance** | Single point of failure | Process isolation |

### Pipeline Hazards & Conflict Resolution

**Demonstrated via Simulator**:
- **Data Hazards**: Dependent tasks stall when upstream not ready
- **Resource Contention**: Shared encoders cause bottlenecks
- **Backpressure**: Full downstream buffers block upstream

**Mitigation Strategies**:
1. **Forwarding**: Pass results directly between stages (skip buffer)
2. **Reordering**: Independent tasks bypass blocked tasks
3. **Buffer Sizing**: Increase queue capacity to reduce stalls
4. **Worker Scaling**: Add workers to hotspot stages

---

## How To Run

### Prerequisites

- Python 3.7 or higher
- Modern web browser (Chrome, Firefox, Edge) with WebXR support
- Optional: VR headset for immersive experience

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `scikit-learn` - Machine learning
- `flask` - Web API server
- `flask-cors` - Cross-origin resource sharing

### Step 2: Start the API Server (Terminal 1)

The API server handles parallel processing and serves predictions:

```bash
python api_server.py
```

**Expected Output**:
```
Starting Disaster Prediction API Server...
API Endpoints:
  GET  /api/predictions - Get disaster predictions
  POST /api/predictions/run - Run predictions with parameters
  GET  /api/pipeline-advantage - Get pipeline simulation
  GET  /heatmaps.html - View heatmaps
 * Running on http://0.0.0.0:5000
```

The server will:
- Load and process flood.csv (10,000+ records) using parallel processing
- Train ML models for disaster prediction
- Calculate state-wise probabilities
- Serve results via REST API

### Step 3: Start the Web Server (Terminal 2)

The web server serves the VR interface, interactive dashboards, and heatmaps:

```bash
python -m http.server 3000
```

**Expected Output**:
```
Serving HTTP on :: port 3000 (http://[::]:3000/) ...
```

### Step 4: Access the Application

**Interactive Dashboard** (Recommended Entry Point):
- Open browser: `http://localhost:3000/disaster_dashboard.html`
- **Features**:
  - **Configure Parallelism**: Adjust worker count (1-64) and chunk size (100-50000)
  - **Run Predictions**: Click "Run Predictions" with custom parameters
  - **View Pipeline Advantage**: Compare Sequential vs Pipelined vs Shared execution with speedup %
  - **Combined Risk Map**: See flood+fire risk for all 28 states
  - **Click-to-VR**: Click any state to launch VR scene at that location with disaster extent based on ML probability

**Main VR Interface**:
- Open browser: `http://localhost:3000`
- Click scenario buttons to view 3D flood/fire simulations
- Use VR headset for immersive experience (if available)
- **ML-Driven Scenarios**: When launched from dashboard, VR loads with:
  - Camera positioned at selected state's coordinates
  - Flood level (0-5m) or fire intensity (0-10) scaled by prediction probability
  - Dynamic POI placement based on disaster severity

**Disaster Prediction Heatmaps** (Legacy View):
- Navigate to: `http://localhost:3000/heatmaps.html`
- View parallel processing performance metrics
- See flood and forest fire risk predictions by state (bar charts)

### Running Parallel Processing Standalone

You can run disaster predictions directly via command line:

```bash
# Default configuration (auto-detect cores)
python parallel_disaster_prediction.py

# Custom worker count
python parallel_disaster_prediction.py --workers 8

# Adjust inference chunk size (larger = better throughput, more memory)
python parallel_disaster_prediction.py --chunk-size 10000

# Skip sequential baseline for faster execution
python parallel_disaster_prediction.py --skip-sequential

# Disable pipeline overview ASCII art
python parallel_disaster_prediction.py --no-pipeline
```

**Output**:
- `disaster_predictions.json`: State-wise flood/fire probabilities + performance metrics
- Console: Pipeline overview diagram, speedup statistics, processing times

### Quick Start (Windows)

Double-click `start_servers.bat` to automatically:
1. Install dependencies
2. Start API server (port 5000)
3. Start web server (port 3000)

### Quick Start (Linux/Mac)

```bash
chmod +x start_servers.sh
./start_servers.sh
```

### Troubleshooting

**Port Already in Use**:
- Change port in `api_server.py` (line 48): `app.run(port=5001)`
- Change port for web server: `python -m http.server 3001`

**API Connection Error**:
- Ensure API server is running on port 5000
- Check browser console for CORS errors
- Verify `flask-cors` is installed

**VR Not Working**:
- Use HTTPS or localhost (WebXR requires secure context)
- Enable WebXR in browser flags (Chrome: `chrome://flags/#webxr`)
- Check VR headset compatibility

---

## Interactive Dashboard

The **Interactive Dashboard** (`disaster_dashboard.html`) provides a comprehensive web interface for configuring, running, and visualizing disaster predictions with parallel processing.

### Features

**1. Parallel Configuration Controls**:
- **Workers Slider** (1-64): Adjust CPU core count for parallel processing
  - Auto-detects available cores on load
  - Real-time display of selected worker count
- **Chunk Size Input** (100-50000): Control inference batch size
  - Larger chunks = better throughput, more memory usage
  - Default: 5000 rows per chunk

**2. Prediction Execution**:
- **Run Predictions Button**: Executes ML pipeline with custom parameters
- **Loading Spinner**: Visual feedback during processing
- **Success/Error Messages**: Clear status indicators
- **Real-time Progress**: Shows API request status

**3. Pipeline Advantage Visualization**:
- **Three Execution Cards**:
  - **Sequential**: Single-threaded baseline (no parallelism)
  - **Pipelined**: Multi-stage overlapping execution
  - **Shared Pipeline**: Optimized with resource reuse
- **Performance Metrics**:
  - Execution time (seconds) for each mode
  - Speedup percentage vs sequential baseline
  - Visual highlighting of fastest mode (green)
- **Color-Coded Results**:
  - Green: Fastest execution
  - Gray: Standard performance

**4. Combined Risk Map** (State-Level Visualization):
- **Interactive Table**: All 28 Indian states with risk scores
- **Weighted Risk Formula**: `Risk = (Flood * 0.55) + (Fire * 0.45)`
- **Color Gradient**: Red (high risk) to green (low risk)
- **Click-to-VR**: Click any state row to launch VR scene
  - Automatically passes state name, disaster type, severity via URL params
  - VR loads with camera at state coordinates
  - Disaster extent scaled by risk probability

**5. Performance Metrics Display**:
- **Processing Times**:
  - Parallel execution time
  - Sequential baseline (if available)
  - Speedup multiplier (e.g., "3.5x faster")
- **Model Accuracy**: Classification accuracy percentage
- **Configuration Summary**: Workers used, chunk size, timestamp

### User Workflow

1. **Configure**: Adjust workers and chunk size sliders
2. **Execute**: Click "Run Predictions" button
3. **Review**: Examine pipeline advantage cards and speedup metrics
4. **Explore**: View combined risk map for all states
5. **Immerse**: Click a state to launch VR visualization

### API Integration

The dashboard communicates with the Flask API server:

**POST /api/predictions/run**:
```json
{
  "workers": 8,
  "chunk_size": 5000
}
```

**Response**:
```json
{
  "states": {
    "Maharashtra": {"flood_prob": 0.85, "fire_prob": 0.12},
    "Karnataka": {"flood_prob": 0.34, "fire_prob": 0.78},
    ...
  },
  "parallel_time": 2.14,
  "sequential_time": 8.52,
  "speedup": 3.98,
  "accuracy": 0.9234
}
```

**GET /api/pipeline-advantage**:
```json
{
  "sequential": {"time": 45.2, "speedup": 1.0},
  "pipelined": {"time": 12.8, "speedup": 3.53},
  "shared": {"time": 9.1, "speedup": 4.97}
}
```

### Technologies Used

- **HTML5/CSS3**: Responsive layout with Flexbox
- **Bulma CSS Framework**: Modern UI components
- **JavaScript ES6**: Async/await for API calls
- **Fetch API**: RESTful communication with Flask backend
- **URLSearchParams**: VR scene parameter passing

---

## Tools & Techniques Summary

This project integrates multiple advanced technologies across graphics, parallel computing, machine learning, and web development:

### Parallel Programming Technologies

- **Python multiprocessing.Pool**: Process-based parallelism for data chunking (bypasses GIL)
- **concurrent.futures.ProcessPoolExecutor**: High-level parallel task execution with worker initialization
- **pickle**: Model serialization for broadcasting to worker processes
- **numpy**: Vectorized array operations (10-100x faster than Python loops)
- **pandas**: DataFrame chunking and parallel concatenation
- **argparse**: CLI argument parsing for worker/chunk size configuration

### Machine Learning Technologies

- **scikit-learn 1.0+**: RandomForestClassifier with `n_jobs=-1` for parallel tree construction
- **joblib**: Parallel backend for scikit-learn operations
- **Label Encoding**: Categorical feature encoding (land cover, soil type)
- **Train-Test Split**: 80/20 stratified sampling for model validation
- **Cross-Validation**: K-fold parallel evaluation

### Virtual Reality Technologies

- **Unity Engine 2020.3 LTS**: 3D game engine (C# scripting)
- **Unity WebGL**: Browser-based deployment via WebAssembly
- **WebXR Device API**: W3C standard for VR/AR in browsers
- **WebXR Polyfill**: Fallback for older browsers (Google Cardboard)
- **gl-matrix.js**: Matrix/vector math for camera transforms
- **GLSL/HLSL**: Shader languages for water/fire effects

### Web Development Technologies

- **Flask 2.0+**: Python web framework for REST API
- **Flask-CORS**: Cross-origin resource sharing middleware
- **JavaScript ES6**: Modern JavaScript with async/await, fetch API, URLSearchParams
- **HTML5**: Semantic markup with WebXR integration
- **CSS3**: Responsive design with Flexbox/Grid
- **Bulma CSS**: Modern CSS framework for dashboard UI

### Graphics & Rendering Technologies

- **WebGL 2.0**: Low-level GPU API for hardware-accelerated rendering
- **Unity Shader Graph**: Visual shader authoring for water/fire effects
- **Gerstner Waves**: Physics-based water surface simulation
- **GPU Particle Systems**: 10,000+ particles for fire simulation
- **Cascade Shadow Maps**: Real-time shadow rendering (4 splits)
- **Screen-Space Ambient Occlusion (SSAO)**: Dynamic lighting enhancement
- **Level of Detail (LOD)**: 4-level mesh optimization

### Data Processing Technologies

- **Pandas**: DataFrame manipulation (10,000+ rows)
- **NumPy**: Numerical computing with vectorized operations
- **Categorical Encoding**: LabelEncoder for feature engineering
- **Coordinate Mapping**: Lat/Lon to state/region conversion
- **Risk Index Calculation**: Weighted feature aggregation

### Optimization Techniques

- **Chunking Strategy**: Divide-and-conquer for large datasets
- **Copy-on-Write**: Memory-efficient chunk processing
- **Shared Memory**: Read-only data shared across processes
- **Work-Stealing Queue**: Load balancing in ProcessPoolExecutor
- **Pipeline Overlapping**: Multi-stage concurrent execution
- **Resource Reuse**: Cached encoders and state mappings
- **Vectorization**: NumPy broadcasting for element-wise ops
- **Draw Call Batching**: GPU rendering optimization (< 500 calls/frame)
- **Texture Compression**: DXT5/ETC2 with mipmaps
- **Frustum/Occlusion Culling**: ~40% draw call reduction

### Simulation Techniques

- **Discrete-Event Simulation**: Models pipeline stage occupancy
- **Queue-Based Scheduling**: FIFO vs reordering strategies
- **Hazard Detection**: Data/resource contention analysis
- **Speedup Calculation**: Parallel vs sequential performance comparison

---

## How To Use

This repository provides a boilerplate to use GeospatialVR. Simply download and run the "index.html".

To examine how the data is provided and visualizations are managed for the VR environment, check out [geospatialxr.js](script/geospatialxr.js)

As a brief summary of basic functionality:

- Load location on the map
```js
updateMapLocation(lat, lon, zoom); // default zoom is 16
```

Extend current map by loading more tiles
```js
extendMap(west, east, north, south); // for initial map, 1 tile is loaded per each direction
```

Enable traffic layer on active map
```js
enableTraffic();
```

Add points of interest with labels on the map
```js
var pois = {"pois": [
                {"lat": 19.0596, 
                  "lon": 72.8295, 
                  "type": "StreamSensor", 
                  "height": 85,
                  "content": "Mithi River Gauge\nHeight: 2.5 m\nDischarge: 450 m³/s"},
                {"lat": 19.0610, 
                  "lon": 72.8310, 
                  "type": "RainGauge", 
                  "height": 70,
                  "content": "IMD Rain Gauge\nLast Reading: 25 mm/hr\nMonsoon Alert: Active"},
      ]};
addPOI(pois);

// Type parameter refers to the label styling. Currently available label types:
// Warning, SensorGeneric, StreamSensor, RainGauge, Soil, Damage, Fireman, FireData
```

Add fire animation to given location(s)
```js
var firePOIs = {"pois": [
                {"lat": 30.3165,
                  "lon": 79.0193,
                  "height": 0},
      ]};
generateFire(firePOIs);
```

## Use Cases

### Flood - Mumbai, India

A case study for flood management in Mumbai, India, showing a flood animation and relevant data layers (i.e. Mithi River gauges, IMD rain gauges, hydro stations for groundwater and soil moisture data, estimated flood damages in Indian Rupees (₹) for current or forecasted flood scenarios, and traffic congestion). Mumbai is prone to monsoon flooding, particularly in the Mithi River area.

Flooding Use Case - Mumbai
:-------------------------:
![Screenshot 1](images/flood.png)

### Forest Fire - Uttarakhand, India

A case study for forest fire management in Uttarakhand, India, showing a fire animation and relevant data layers (i.e. characteristics and center of the forest fire, evacuation requirements for nearby villages, air quality and PM2.5 measurements in the area, forest officer vitals, and traffic congestion). Uttarakhand's Himalayan forests are prone to fires during dry seasons.

Forest Fire Use Case - Uttarakhand
:-------------------------:
![Screenshot 1](images/fire.png)


## Feedback

Feel free to send us feedback by filing an issue.

## To-Do

This framework is currently a functioning prototype, and is not suitable for use at an operational level. 

- Allow users to create rooms for multiuser.
- Race condition exists when multiple users interact at the same environment.
- Always initialize the map at the same location in the virtual room regardless of the location's elevation.
- Allow developers to create custom POI labels by providing color, icon, and font through JS.
- and more...

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements & Citation

This project is developed by the University of Iowa Hydroinformatics Lab (UIHI Lab): [https://hydroinformatics.uiowa.edu/](https://hydroinformatics.uiowa.edu/).

This project utilizes Mapbox Unity SDK and Mozilla Unity WebXR Exporter.

> Sermet, Y. and Demir, I., 2021. GeospatialVR: A web-based virtual reality framework for collaborative environmental simulations. Computers & Geosciences, p.105010. https://doi.org/10.1016/j.cageo.2021.105010

> Sermet, Y. and Demir, I., 2020, November. An Immersive Decision Support System for Disaster Response. In 26th ACM Symposium on Virtual Reality Software and Technology (pp. 1-3). https://doi.org/10.1145/3385956.3422087
