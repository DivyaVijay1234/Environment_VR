# Parallel Processing for Disaster Prediction

This project implements parallel processing to predict flood and forest fire risks for Indian states using machine learning.

## Features

- **Parallel Data Processing**: Uses Python multiprocessing to analyze large datasets
- **ML-based Predictions**: Random Forest classifier for flood prediction
- **State-wise Heatmaps**: Visual representation of disaster probabilities
- **Performance Metrics**: Comparison of parallel vs sequential processing

## Setup

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the API Server**:
```bash
python api_server.py
```
The server will start on `http://localhost:5000`

3. **Run the Main Application**:
```bash
python -m http.server 3000
```

4. **Access the Application**:
- Main VR Interface: `http://localhost:3000`
- Heatmaps Page: `http://localhost:3000/heatmaps.html` or click "View State-wise Predictions" button

## How It Works

### Parallel Processing Pipeline

1. **Data Loading**: Loads `flood.csv` (10,000+ records) and `forestfire.csv`
2. **Data Chunking**: Splits data into chunks based on CPU cores
3. **Parallel Processing**: Each chunk is processed simultaneously:
   - Coordinate to state mapping
   - Feature encoding
   - Data transformation
4. **Model Training**: Random Forest classifier with parallel tree construction
5. **Prediction**: State-wise probability calculation

### Performance Improvement

The parallel implementation shows significant speedup:
- **Sequential**: Processes data one chunk at a time
- **Parallel**: Processes multiple chunks simultaneously using all CPU cores
- **Speedup**: Typically 2-4x faster depending on CPU cores

## API Endpoints

- `GET /api/predictions` - Get disaster predictions
- `POST /api/predictions/refresh` - Refresh predictions (recalculate)
- `GET /heatmaps.html` - View heatmaps page

## Files

- `parallel_disaster_prediction.py` - Main parallel processing script
- `api_server.py` - Flask API server
- `heatmaps.html` - Frontend visualization page
- `flood.csv` - Flood dataset (10,002 records)
- `forestfire.csv` - Forest fire dataset (37 states)

