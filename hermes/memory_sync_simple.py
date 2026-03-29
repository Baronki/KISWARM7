#!/usr/bin/env python3
"""Simple Memory Sync API on port 5002"""

from flask import Flask, request, jsonify
import json, os
from datetime import datetime

app = Flask(__name__)
MEMORY_DIR = "/opt/hermes/memory/longterm"
EDGE_STATE_DIR = "/opt/hermes/state/edges"
os.makedirs(EDGE_STATE_DIR, exist_ok=True)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "memory_sync", "port": 5002})

@app.route('/api/memory/sync', methods=['POST'])
def sync():
    return jsonify({"status": "synced"})

@app.route('/api/memory/export')
def export():
    return jsonify({"memories": [], "count": 0})

@app.route('/api/edge/register', methods=['POST'])
def register():
    return jsonify({"status": "registered"})

@app.route('/api/edge/list')
def list_edges():
    return jsonify({"edges": [], "count": 0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
