"""
Flask API server to serve disaster predictions and heatmap data
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import json
import os
from parallel_disaster_prediction import predict_disasters_parallel
from pipeline_simulator import demo_pipeline_advantage_dict

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Cache for predictions
predictions_cache = None

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """Get disaster predictions (flood and forest fire)"""
    global predictions_cache
    
    if predictions_cache is None:
        # Generate predictions
        predictions_cache = predict_disasters_parallel(show_pipeline=False)
    
    return jsonify(predictions_cache)

@app.route('/api/predictions/run', methods=['POST'])
def run_predictions():
    """Run predictions with custom parameters"""
    global predictions_cache
    
    # Get parameters from request
    data = request.get_json() or {}
    workers = data.get('workers', None)
    chunk_size = data.get('chunk_size', 5000)
    skip_sequential = data.get('skip_sequential', True)
    show_pipeline = data.get('show_pipeline', True)
    
    # Convert workers to int if provided
    if workers is not None:
        workers = int(workers)
    
    # Run predictions with specified parameters
    predictions_cache = predict_disasters_parallel(
        n_workers=workers,
        inference_chunk_size=chunk_size,
        run_sequential=not skip_sequential,
        show_pipeline=show_pipeline
    )
    
    return jsonify({
        'status': 'success',
        'predictions': predictions_cache,
        'params_used': {
            'workers': workers,
            'chunk_size': chunk_size,
            'skip_sequential': skip_sequential,
            'show_pipeline': show_pipeline
        }
    })

@app.route('/api/predictions/refresh', methods=['POST'])
def refresh_predictions():
    """Refresh predictions by recalculating"""
    global predictions_cache
    predictions_cache = predict_disasters_parallel(show_pipeline=False)
    return jsonify(predictions_cache)

@app.route('/heatmaps.html')
def heatmaps():
    """Serve the heatmaps page"""
    return send_from_directory('.', 'heatmaps.html')

@app.route('/disaster_dashboard.html')
def dashboard():
    """Serve the disaster prediction dashboard"""
    return send_from_directory('.', 'disaster_dashboard.html')

@app.route('/api/pipeline-advantage', methods=['GET'])
def get_pipeline_advantage():
    """Get pipeline simulator results showing sequential vs pipelined execution"""
    results = demo_pipeline_advantage_dict()
    return jsonify(results)

@app.route('/favicon.ico')
def favicon():
    """Return a blank favicon to suppress 404 errors"""
    return '', 204

@app.route('/')
def index():
    """Serve the disaster dashboard at root"""
    return send_from_directory('.', 'disaster_dashboard.html')

if __name__ == '__main__':
    print("Starting Disaster Prediction API Server...")
    print("API Endpoints:")
    print("  GET  /api/predictions - Get disaster predictions")
    print("  POST /api/predictions/run - Run predictions with custom parameters")
    print("  POST /api/predictions/refresh - Refresh predictions")
    print("  GET  /heatmaps.html - View heatmaps")
    print("  GET  /disaster_dashboard.html - View disaster dashboard (RECOMMENDED)")
    app.run(host='0.0.0.0', port=5000, debug=True)

