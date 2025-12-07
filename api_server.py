"""
Flask API server to serve disaster predictions and heatmap data
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from parallel_disaster_prediction import predict_disasters_parallel

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
        predictions_cache = predict_disasters_parallel()
    
    return jsonify(predictions_cache)

@app.route('/api/predictions/refresh', methods=['POST'])
def refresh_predictions():
    """Refresh predictions by recalculating"""
    global predictions_cache
    predictions_cache = predict_disasters_parallel()
    return jsonify(predictions_cache)

@app.route('/heatmaps.html')
def heatmaps():
    """Serve the heatmaps page"""
    return send_from_directory('.', 'heatmaps.html')

if __name__ == '__main__':
    print("Starting Disaster Prediction API Server...")
    print("API Endpoints:")
    print("  GET  /api/predictions - Get disaster predictions")
    print("  POST /api/predictions/refresh - Refresh predictions")
    print("  GET  /heatmaps.html - View heatmaps")
    app.run(host='0.0.0.0', port=5000, debug=True)

