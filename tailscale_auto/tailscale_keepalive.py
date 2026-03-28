#!/usr/bin/env python3
"""
🔄 TAILSCALE AUTO-RECONNECT SYSTEM
Purpose: Automatically maintain Tailscale connection for GLM environment
Features:
- Periodic connection checks
- Auto-reconnect on disconnection
- Health monitoring
- Mesh status reporting to KISWARM
"""

import os
import sys
import json
import logging
import subprocess
import time
import requests
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [TAILSCALE-KEEPALIVE] %(message)s'
)
logger = logging.getLogger('TAILSCALE')

class TailscaleKeepAlive:
    """Automatic Tailscale connection manager"""
    
    # Paths
    TAILSCALE_BIN = '/home/z/my-project/bin/tailscale'
    TAILSCALED_BIN = '/home/z/my-project/bin/tailscaled'
    STATE_DIR = '/home/z/my-project/tailscale-state'
    SOCKET_PATH = '/tmp/tailscaled.sock'
    
    # Auth key (from credentials)
    AUTH_KEY = 'tskey-auth-kYzoboKgtK11CNTRL-cAh5zWNeygaKa2LEtAg8haF773px2SjY'
    
    # Mesh nodes
    MESH_NODES = {
        'upcloud': '100.112.181.6',
        'openclaw': '100.113.1.85',
        'sah6': '100.92.174.24',
        'glm': '100.79.42.15'
    }
    
    # KISWARM reporting
    KISWARM_EXECUTE = 'http://95.111.212.112:5556/execute'
    AUTH_TOKEN = 'ada6952188dce59c207b9a61183e8004'
    
    def __init__(self):
        self.connected = False
        self.last_check = None
        self.reconnect_count = 0
        self.check_interval = 60  # seconds
        
        # Ensure state directory exists
        Path(self.STATE_DIR).mkdir(parents=True, exist_ok=True)
        
    def is_tailscaled_running(self) -> bool:
        """Check if tailscaled daemon is running"""
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'tailscaled'],
                capture_output=True, text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def start_tailscaled(self) -> bool:
        """Start tailscaled daemon"""
        if self.is_tailscaled_running():
            logger.info("tailscaled already running")
            return True
        
        try:
            # Start tailscaled with user socket
            cmd = f'{self.TAILSCALED_BIN} --state={self.STATE_DIR}/tailscaled.state --socket={self.SOCKET_PATH} &'
            subprocess.run(cmd, shell=True, capture_output=True)
            
            # Wait for socket to be ready
            for _ in range(10):
                if os.path.exists(self.SOCKET_PATH):
                    logger.info("✅ tailscaled started")
                    return True
                time.sleep(1)
            
            logger.error("tailscaled socket not ready after 10s")
            return False
            
        except Exception as e:
            logger.error(f"Failed to start tailscaled: {e}")
            return False
    
    def check_connection(self) -> bool:
        """Check if connected to Tailscale mesh"""
        try:
            result = subprocess.run(
                [self.TAILSCALE_BIN, '--socket', self.SOCKET_PATH, 'status'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # Parse status output
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if '100.' in line:  # Tailscale IP found
                        self.connected = True
                        self.last_check = datetime.now().isoformat()
                        return True
            
            self.connected = False
            return False
            
        except Exception as e:
            logger.debug(f"Connection check failed: {e}")
            self.connected = False
            return False
    
    def connect(self) -> bool:
        """Connect to Tailscale network"""
        if self.check_connection():
            logger.info("Already connected to Tailscale")
            return True
        
        try:
            # Run tailscale up with auth key
            result = subprocess.run(
                [self.TAILSCALE_BIN, '--socket', self.SOCKET_PATH, 'up', 
                 '--authkey', self.AUTH_KEY, '--accept-routes'],
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode == 0 or 'already' in result.stderr.lower():
                self.connected = True
                self.reconnect_count += 1
                logger.info(f"✅ Connected to Tailscale (reconnect #{self.reconnect_count})")
                return True
            else:
                logger.error(f"Connection failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def ping_mesh(self) -> dict:
        """Ping all mesh nodes"""
        results = {}
        
        for name, ip in self.MESH_NODES.items():
            try:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '2', ip],
                    capture_output=True, text=True, timeout=5
                )
                results[name] = {
                    'ip': ip,
                    'reachable': result.returncode == 0,
                    'last_check': datetime.now().isoformat()
                }
            except:
                results[name] = {
                    'ip': ip,
                    'reachable': False,
                    'last_check': datetime.now().isoformat()
                }
        
        return results
    
    def report_to_kiswarm(self, status: dict):
        """Report status to KISWARM master"""
        try:
            requests.post(
                self.KISWARM_EXECUTE,
                headers={
                    'Content-Type': 'application/json',
                    'X-Auth-Token': self.AUTH_TOKEN
                },
                json={
                    'command': f'echo \'{json.dumps(status)}\' > /opt/kiswarm7/data/glm_sync/tailscale_status.json'
                },
                timeout=10
            )
        except Exception as e:
            logger.debug(f"Failed to report to KISWARM: {e}")
    
    def get_status(self) -> dict:
        """Get current status"""
        return {
            'connected': self.connected,
            'last_check': self.last_check,
            'reconnect_count': self.reconnect_count,
            'tailscaled_running': self.is_tailscaled_running(),
            'mesh_ping': self.ping_mesh() if self.connected else {}
        }
    
    def run_keepalive(self):
        """Main keepalive loop"""
        logger.info("🔄 Starting Tailscale KeepAlive System")
        
        while True:
            try:
                # Ensure tailscaled is running
                if not self.start_tailscaled():
                    logger.error("Cannot start tailscaled, retrying in 30s")
                    time.sleep(30)
                    continue
                
                # Check connection
                if not self.check_connection():
                    logger.warning("Disconnected, attempting reconnect...")
                    self.connect()
                
                # Report status
                status = self.get_status()
                self.report_to_kiswarm(status)
                logger.info(f"Status: connected={self.connected}, mesh={len([r for r in status['mesh_ping'].values() if r.get('reachable')])} nodes")
                
                # Wait for next check
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("KeepAlive stopped by user")
                break
            except Exception as e:
                logger.error(f"KeepAlive error: {e}")
                time.sleep(30)


# Flask API for status
from flask import Flask, jsonify

app = Flask(__name__)
keepalive = TailscaleKeepAlive()

@app.route('/')
def index():
    return jsonify({
        'name': 'Tailscale-KeepAlive',
        'version': '1.0',
        'status': keepalive.get_status()
    })

@app.route('/status')
def status():
    return jsonify(keepalive.get_status())

@app.route('/connect', methods=['POST'])
def connect():
    result = keepalive.connect()
    return jsonify({'connected': result})

@app.route('/mesh')
def mesh():
    return jsonify(keepalive.ping_mesh())

if __name__ == '__main__':
    import threading
    
    # Start keepalive in background
    keepalive_thread = threading.Thread(target=keepalive.run_keepalive, daemon=True)
    keepalive_thread.start()
    
    # Start Flask API
    logger.info("🌐 Starting Tailscale KeepAlive API on port 5201")
    app.run(host='127.0.0.1', port=5201)
