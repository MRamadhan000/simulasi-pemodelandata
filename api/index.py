"""
Vercel Serverless API for Simulasi Verifikasi Pembayaran Digital
================================================================
Flask-based API that exposes DES + Monte Carlo simulation as REST endpoints.
"""

import sys
import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
from flask import Flask, request, jsonify, Response

# Add project root to path so we can import simulation module
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from simulation.des import DESSimulation, get_server_state_at_time
from simulation.monte_carlo import MonteCarloSimulation

app = Flask(__name__)

DATA_DIR = PROJECT_ROOT / "data"


# ======================== HELPERS ========================

def load_dataset(scenario_key):
    """Load dataset dari file JSON"""
    filepath = DATA_DIR / f"{scenario_key}_dataset.json"
    if filepath.exists():
        with open(filepath, 'r') as f:
            return json.load(f)
    return None


def load_all_datasets():
    """Load semua dataset yang tersedia"""
    scenario_keys = ['sepi', 'normal', 'padat', 'sangat_padat']
    datasets = {}
    for key in scenario_keys:
        data = load_dataset(key)
        if data:
            datasets[key] = data
    return datasets


def json_to_dataframe(json_data):
    """Convert JSON dataset ke DataFrame untuk simulasi"""
    transactions = json_data['transactions']
    df = pd.DataFrame([{
        'Transaction_ID': tx['transaction_id'],
        'Interarrival_Time': tx['interarrival_time'],
        'Verification_Time': tx['verification_time']
    } for tx in transactions])
    return df


def convert_numpy(obj):
    """Recursively convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(v) for v in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient='records')
    return obj


# ======================== API ROUTES ========================

@app.route('/api/datasets', methods=['GET'])
def get_datasets():
    """List semua dataset yang tersedia"""
    datasets = load_all_datasets()
    result = {}
    for key, data in datasets.items():
        result[key] = {
            'scenario_name': data['scenario_name'],
            'description': data['description'],
            'statistics': data['statistics'],
            'metadata': data['metadata']
        }
    return jsonify(result)


@app.route('/api/dataset/<scenario>', methods=['GET'])
def get_dataset(scenario):
    """Ambil detail dataset lengkap (termasuk transaksi)"""
    data = load_dataset(scenario)
    if data is None:
        return jsonify({'error': f'Dataset {scenario} tidak ditemukan'}), 404
    return jsonify(data)


@app.route('/api/simulate', methods=['POST'])
def run_simulation():
    """
    Jalankan simulasi DES + Monte Carlo.
    
    Request Body (JSON):
    {
        "scenario": "normal",           // atau null jika custom data
        "custom_data": [...],            // optional: array of {Transaction_ID, Interarrival_Time, Verification_Time}
        "num_servers": 4,
        "mc_iterations": 100,
        "vt_min": 2,
        "vt_max": 6
    }
    
    Returns: JSON with DES results, MC aggregated metrics, and MC per-iteration metrics
    """
    try:
        body = request.get_json()
        
        scenario = body.get('scenario')
        custom_data = body.get('custom_data')
        num_servers = body.get('num_servers', 4)
        mc_iterations = body.get('mc_iterations', 100)
        vt_min = body.get('vt_min', 2)
        vt_max = body.get('vt_max', 6)
        
        # Limit iterations to prevent timeout (Vercel free tier = 10s)
        mc_iterations = min(mc_iterations, 500)
        num_servers = max(1, min(num_servers, 8))
        
        # Build DataFrame
        if custom_data:
            df = pd.DataFrame(custom_data)
            # Ensure correct column names
            if 'Transaction_ID' not in df.columns:
                return jsonify({'error': 'custom_data harus punya kolom Transaction_ID'}), 400
            if 'Interarrival_Time' not in df.columns:
                return jsonify({'error': 'custom_data harus punya kolom Interarrival_Time'}), 400
            if 'Verification_Time' not in df.columns:
                return jsonify({'error': 'custom_data harus punya kolom Verification_Time'}), 400
        elif scenario:
            data = load_dataset(scenario)
            if data is None:
                return jsonify({'error': f'Dataset {scenario} tidak ditemukan'}), 404
            df = json_to_dataframe(data)
        else:
            return jsonify({'error': 'Harus menyertakan scenario atau custom_data'}), 400
        
        # ---- Single DES Run ----
        des = DESSimulation(num_servers=num_servers)
        des_results = des.run_simulation(df)
        
        # ---- Monte Carlo ----
        mc = MonteCarloSimulation(num_iterations=mc_iterations, num_servers=num_servers)
        mc.run_monte_carlo(df, vt_min=vt_min, vt_max=vt_max)
        aggregated, metrics_df = mc.get_aggregated_metrics()
        
        # Build time points for real-time view
        time_points = sorted(set(
            list(des_results['Arrival_Time'].values) +
            list(des_results['Start_Time'].values) +
            list(des_results['End_Time'].values)
        ))
        if len(time_points) > 20:
            step = len(time_points) // 20
            time_points = time_points[::step]
        
        # Build server states for each time point
        server_states = {}
        for t in time_points:
            t_rounded = round(float(t), 2)
            server_status, queue = get_server_state_at_time(des_results, t_rounded, num_servers)
            server_states[str(t_rounded)] = {
                'servers': convert_numpy(server_status),
                'queue': convert_numpy(queue)
            }
        
        response = {
            'des_results': convert_numpy(des_results.to_dict(orient='records')),
            'mc_aggregated': convert_numpy(aggregated),
            'mc_metrics': convert_numpy(metrics_df.to_dict(orient='records')),
            'time_points': [round(float(t), 2) for t in time_points],
            'server_states': server_states,
            'params': {
                'num_servers': num_servers,
                'mc_iterations': mc_iterations,
                'vt_min': vt_min,
                'vt_max': vt_max
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Simulasi API is running'})


# Vercel expects the Flask app as `app`
