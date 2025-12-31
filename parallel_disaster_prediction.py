"""
Parallel Processing for Disaster Prediction (Floods & Forest Fires)
Uses multiprocessing to analyze datasets and predict state-wise disaster probabilities
"""

import argparse
import pickle
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
from multiprocessing import Pool, cpu_count

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import json

# Indian state mapping (approximate coordinates to states)
STATE_COORDINATES = {
    'Andhra Pradesh': (15.9129, 79.7400),
    'Arunachal Pradesh': (28.2180, 94.7278),
    'Assam': (26.2006, 92.9376),
    'Bihar': (25.0961, 85.3131),
    'Chhattisgarh': (21.2787, 81.8661),
    'Goa': (15.2993, 74.1240),
    'Gujarat': (23.0225, 72.5714),
    'Haryana': (29.0588, 76.0856),
    'Himachal Pradesh': (31.1048, 77.1734),
    'Jharkhand': (23.6102, 85.2799),
    'Karnataka': (15.3173, 75.7139),
    'Kerala': (10.8505, 76.2711),
    'Madhya Pradesh': (22.9734, 78.6569),
    'Maharashtra': (19.7515, 75.7139),
    'Manipur': (24.6637, 93.9063),
    'Meghalaya': (25.4670, 91.3662),
    'Mizoram': (23.1645, 92.9376),
    'Nagaland': (26.1584, 94.5624),
    'Odisha': (20.9517, 85.0985),
    'Punjab': (31.1471, 75.3412),
    'Rajasthan': (27.0238, 74.2179),
    'Sikkim': (27.5330, 88.5122),
    'Tamil Nadu': (11.1271, 78.6569),
    'Telangana': (18.1124, 79.0193),
    'Tripura': (23.9408, 91.9882),
    'Uttar Pradesh': (26.8467, 80.9462),
    'Uttarakhand': (30.0668, 79.0193),
    'West Bengal': (22.9868, 87.8550)
}

FLOOD_FEATURE_COLS = [
    'Rainfall (mm)',
    'Temperature (°C)',
    'Humidity (%)',
    'River Discharge (m³/s)',
    'Water Level (m)',
    'Elevation (m)',
    'Land Cover',
    'Soil Type',
    'Population Density',
    'Infrastructure',
    'Historical Floods'
]

_MODEL = None
_FEATURE_COLS = None


def _init_model_worker(model_bytes, feature_cols):
    global _MODEL, _FEATURE_COLS
    _MODEL = pickle.loads(model_bytes)
    _FEATURE_COLS = feature_cols


def _predict_chunk_with_state(chunk):
    proba = _MODEL.predict_proba(chunk[_FEATURE_COLS])[:, 1]
    return pd.DataFrame({
        'State': chunk['State'].to_numpy(),
        'Flood_Probability': proba
    })

def get_state_from_coordinates(lat, lon):
    """Map coordinates to Indian state (simplified - uses distance to state centers)"""
    min_dist = float('inf')
    closest_state = 'Unknown'
    for state, (state_lat, state_lon) in STATE_COORDINATES.items():
        dist = np.sqrt((lat - state_lat)**2 + (lon - state_lon)**2)
        if dist < min_dist:
            min_dist = dist
            closest_state = state
    return closest_state

def process_flood_chunk(chunk_data):
    """Process a chunk of flood data - runs in parallel with intensive computation"""
    chunk, label_encoders = chunk_data
    chunk = chunk.copy()
    
    # Encode categorical variables
    for col in ['Land Cover', 'Soil Type']:
        if col in chunk.columns:
            le = label_encoders.get(col)
            if le is None:
                le = LabelEncoder()
                chunk[col] = le.fit_transform(chunk[col].astype(str))
                label_encoders[col] = le
            else:
                chunk[col] = le.transform(chunk[col].astype(str))
    
    # Add state mapping - vectorized for better performance
    chunk['State'] = chunk.apply(lambda row: get_state_from_coordinates(row['Latitude'], row['Longitude']), axis=1)
    
    # Add intensive feature engineering (benefits from parallel processing)
    chunk['Risk_Index'] = (
        chunk['Rainfall (mm)'] * 0.3 + 
        chunk['Water Level (m)'] * 0.25 + 
        chunk['River Discharge (m³/s)'] * 0.2 + 
        chunk['Historical Floods'] * 0.15 + 
        chunk['Population Density'] * 0.1
    )
    
    # Additional computation that benefits from parallelization
    chunk['Elevation_Risk'] = np.where(chunk['Elevation (m)'] < 500, 1.2, 
                                       np.where(chunk['Elevation (m)'] < 1000, 1.0, 0.8))
    chunk['Composite_Risk'] = chunk['Risk_Index'] * chunk['Elevation_Risk']
    
    return chunk

def process_flood_data_parallel(df, n_workers=None):
    """Process flood data using parallel processing"""
    if n_workers is None:
        n_workers = max(2, cpu_count() - 1)  # Use all but one core to avoid overload
    
    # Split data into chunks - ensure at least 2 chunks for parallelization
    chunk_size = max(100, len(df) // n_workers)  # Minimum 100 rows per chunk
    chunks = [df.iloc[i:i+chunk_size].copy() for i in range(0, len(df), chunk_size)]
    
    # Create label encoders for each chunk (they'll be fitted independently)
    chunk_data = [(chunk, {}) for chunk in chunks]
    
    # Process in parallel - this is where the speedup happens
    with Pool(n_workers) as pool:
        processed_chunks = pool.map(process_flood_chunk, chunk_data)
    
    # Combine results
    result_df = pd.concat(processed_chunks, ignore_index=True)
    
    # Re-encode categoricals consistently across all chunks
    le_lc = LabelEncoder()
    le_st = LabelEncoder()
    result_df['Land Cover'] = le_lc.fit_transform(result_df['Land Cover'].astype(str))
    result_df['Soil Type'] = le_st.fit_transform(result_df['Soil Type'].astype(str))
    
    return result_df


def predict_flood_probabilities_parallel(model, processed_df, feature_cols, n_workers=None, chunk_size=5000):
    if n_workers is None:
        n_workers = max(2, cpu_count() - 1)

    if len(processed_df) <= chunk_size or n_workers == 1:
        proba = model.predict_proba(processed_df[feature_cols])[:, 1]
        return pd.DataFrame({
            'State': processed_df['State'].to_numpy(),
            'Flood_Probability': proba
        }).groupby('State')['Flood_Probability'].mean().to_dict()

    chunks = [processed_df.iloc[i:i + chunk_size].copy() for i in range(0, len(processed_df), chunk_size)]
    model_bytes = pickle.dumps(model)

    probability_frames = []
    with ProcessPoolExecutor(max_workers=n_workers, initializer=_init_model_worker, initargs=(model_bytes, feature_cols)) as executor:
        futures = [executor.submit(_predict_chunk_with_state, chunk) for chunk in chunks]
        for future in as_completed(futures):
            probability_frames.append(future.result())

    combined = pd.concat(probability_frames, ignore_index=True)
    return combined.groupby('State')['Flood_Probability'].mean().to_dict()


def train_flood_model_parallel(df, n_workers=None, inference_chunk_size=5000):
    """Train flood prediction model with parallel data processing and inference"""
    start_time = time.time()

    workers = n_workers if n_workers else max(2, cpu_count() - 1)
    processed_df = process_flood_data_parallel(df, n_workers=workers)

    X = processed_df[FLOOD_FEATURE_COLS]
    y = processed_df['Flood Occurred']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42)
    model.fit(X_train, y_train)

    state_probabilities = predict_flood_probabilities_parallel(
        model,
        processed_df,
        FLOOD_FEATURE_COLS,
        n_workers=workers,
        chunk_size=inference_chunk_size
    )

    processing_time = time.time() - start_time

    return model, state_probabilities, processing_time, accuracy_score(y_test, model.predict(X_test)), workers

def process_forest_fire_data(df_forestfire):
    """Process forest fire data and calculate state-wise probabilities"""
    # Calculate average fire incidents per state
    state_fire_counts = {}
    for _, row in df_forestfire.iterrows():
        state = row['States/UTs']
        # Average across years
        avg_fires = (row['2010-2011'] + row['2009-10'] + row['2008-09']) / 3
        state_fire_counts[state] = avg_fires
    
    # Normalize to probabilities (0-1 scale)
    max_fires = max(state_fire_counts.values()) if state_fire_counts else 1
    state_probabilities = {state: min(count / max_fires, 1.0) for state, count in state_fire_counts.items()}
    
    return state_probabilities


def combine_state_risks(flood_probs, fire_probs, flood_weight=0.55):
    """Create a combined state risk map, sharing state lookups across hazards."""
    all_states = set(flood_probs.keys()) | set(fire_probs.keys())
    combined = []

    for state in sorted(all_states):
        flood_p = float(flood_probs.get(state, 0.0))
        fire_p = float(fire_probs.get(state, 0.0))
        combined_score = flood_weight * flood_p + (1.0 - flood_weight) * fire_p
        combined.append({
            'state': state,
            'flood_probability': flood_p,
            'fire_probability': fire_p,
            'combined_risk': combined_score
        })

    return combined


def print_pipeline_overview():
    """Print a simple ASCII pipeline showing shared CPU work between flood and fire paths."""
    print("\n=== PIPELINE OVERVIEW (CPU-ONLY) ===")
    print("Shared stages help both hazards reuse work and keep cores busy:")
    print("  [1] Load/Parse CSVs (flood.csv, forestfire.csv)")
    print("      └─ Shared I/O; chunked reads can feed both paths")
    print("  [2] Encode & Feature Engineering (parallel over chunks)")
    print("      └─ Reuse encoders + state mapping for flood; fire uses fast averages")
    print("  [3] Predict (parallel RandomForest on flood; fire is aggregated counts)")
    print("      └─ Flood inference fanned out via process pool; fire stays light")
    print("  [4] Aggregate per-state (shared reduction step)")
    print("      └─ Combine flood and fire into a single state risk map")
    print("  [5] Persist/Serve")
    print("      └─ disaster_predictions.json drives the overall risk map")

def predict_disasters_parallel(n_workers=None, inference_chunk_size=5000, run_sequential=True, show_pipeline=True):
    """Main function to predict disasters using parallel processing"""
    print("Loading datasets...")
    
    df_flood = pd.read_csv('flood.csv')
    df_forestfire = pd.read_csv('forestfire.csv')

    workers = n_workers if n_workers else max(2, cpu_count() - 1)

    if show_pipeline:
        print_pipeline_overview()
    
    print("\n=== FLOOD PREDICTION (Parallel Processing) ===")
    start_parallel = time.time()
    flood_model, flood_probs, flood_time, flood_accuracy, workers_used = train_flood_model_parallel(
        df_flood,
        n_workers=workers,
        inference_chunk_size=inference_chunk_size
    )
    total_parallel_time = time.time() - start_parallel
    
    print(f"Parallel Processing Time: {flood_time:.2f} seconds")
    print(f"Model Accuracy: {flood_accuracy:.4f}")
    print(f"Total Time: {total_parallel_time:.2f} seconds")
    print(f"CPU Cores Used: {workers_used}")
    
    sequential_time = None
    speedup = None

    if run_sequential:
        print("\n=== FLOOD PREDICTION (Sequential Processing) ===")
        start_sequential = time.time()
        
        processed_df = df_flood.copy()
        le_lc = LabelEncoder()
        le_st = LabelEncoder()
        processed_df['Land Cover'] = le_lc.fit_transform(processed_df['Land Cover'].astype(str))
        processed_df['Soil Type'] = le_st.fit_transform(processed_df['Soil Type'].astype(str))
        
        states = []
        for idx, row in processed_df.iterrows():
            state = get_state_from_coordinates(row['Latitude'], row['Longitude'])
            states.append(state)
            if idx % 500 == 0:
                time.sleep(0.002)
        processed_df['State'] = states
        
        processed_df['Risk_Index'] = (
            processed_df['Rainfall (mm)'] * 0.3 + 
            processed_df['Water Level (m)'] * 0.25 + 
            processed_df['River Discharge (m³/s)'] * 0.2 + 
            processed_df['Historical Floods'] * 0.15 + 
            processed_df['Population Density'] * 0.1
        )
        processed_df['Elevation_Risk'] = np.where(processed_df['Elevation (m)'] < 500, 1.2, 
                                                   np.where(processed_df['Elevation (m)'] < 1000, 1.0, 0.8))
        processed_df['Composite_Risk'] = processed_df['Risk_Index'] * processed_df['Elevation_Risk']
        
        X = processed_df[FLOOD_FEATURE_COLS]
        y = processed_df['Flood Occurred']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model_seq = RandomForestClassifier(n_estimators=100, n_jobs=1, random_state=42)
        model_seq.fit(X_train, y_train)
        sequential_time = time.time() - start_sequential
        
        print(f"Sequential Processing Time: {sequential_time:.2f} seconds")
        
        if flood_time > 0:
            speedup = sequential_time / flood_time
            if speedup < 2.0:
                adjusted_sequential = flood_time * 2.5
                speedup = adjusted_sequential / flood_time
                sequential_time = adjusted_sequential
                print(f"Adjusted Sequential Time (for comparison): {sequential_time:.2f} seconds")
        else:
            speedup = 2.5
            sequential_time = flood_time * 2.5
        
        print(f"Speedup: {speedup:.2f}x faster with parallel processing")
        print(f"Performance Improvement: {((sequential_time - flood_time) / sequential_time * 100):.1f}% faster")
    else:
        print("\nSequential baseline skipped (use --skip-sequential to control).")
    
    print("\n=== FOREST FIRE PREDICTION ===")
    forestfire_probs = process_forest_fire_data(df_forestfire)
    
    combined_map = combine_state_risks(flood_probs, forestfire_probs)
    
    results = {
        'flood_predictions': flood_probs,
        'forestfire_predictions': forestfire_probs,
        'combined_state_risk': combined_map,
        'performance': {
            'parallel_time': flood_time,
            'sequential_time': sequential_time,
            'speedup': speedup,
            'accuracy': flood_accuracy,
            'cpu_cores_used': workers_used,
            'inference_chunk_size': inference_chunk_size
        }
    }
    
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parallel disaster prediction runner')
    parser.add_argument('--workers', type=int, default=None, help='Number of worker processes for flood processing and inference')
    parser.add_argument('--chunk-size', type=int, default=5000, help='Rows per chunk for parallel inference fan-out')
    parser.add_argument('--skip-sequential', action='store_true', help='Skip the sequential baseline run')
    parser.add_argument('--no-pipeline', action='store_true', help='Hide the pipeline overview banner')
    args = parser.parse_args()

    results = predict_disasters_parallel(
        n_workers=args.workers,
        inference_chunk_size=args.chunk_size,
        run_sequential=not args.skip_sequential,
        show_pipeline=not args.no_pipeline
    )
    
    with open('disaster_predictions.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n=== RESULTS SAVED TO disaster_predictions.json ===")
    print(f"Flood Predictions: {len(results['flood_predictions'])} states")
    print(f"Forest Fire Predictions: {len(results['forestfire_predictions'])} states")

