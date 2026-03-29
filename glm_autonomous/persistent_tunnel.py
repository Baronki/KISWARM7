#!/usr/bin/env python3
"""
🌀 GLM PERSISTENT TUNNEL SERVICE v2.0
=====================================
Bidirectional persistent connection to KISWARM network

Capabilities:
- SSH tunnel to UpCloud Master
- Execute API fallback
- Local API server (port 5557)
- Telegram notifications
- Auto-reconnect on failure
"""

import os
import sys
import json
import time
import logging
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests
import paramiko
from flask import Flask, request, jsonify

# ============================================================
# CONFIGURATION
# ============================================================

LOG_DIR = Path('/home/z/my-project/logs')
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [GLM-TUNNEL] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'persistent_tunnel.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('GLM_TUNNEL')

# Credentials
CREDENTIALS = {
    'upcloud_public_ip': '95.111.212.112',
    'upcloud_tailscale_ip': '100.112.181.6',
    'execute_api_port': 5556,
    'local_api_port': 5557,
    'auth_token': 'ada6952188dce59c207b9a61183e8004',
    'ssh_key_path': '/home/z/.ssh/id_ed25519',
    'ssh_user': 'root',
    'telegram_token': '8519794034:AAFlFNXCXiYeJNGXif1sbVJrU5bgDNQzuPk',
    'admin_chat_id': '1615268492'
}

# Mesh nodes
MESH_NODES = {
    'master': {
        'public_ip': '95.111.212.112',
        'tailscale_ip': '100.112.181.6',
        'role': 'PRIMARY'
    },
    'glm': {
        'tailscale_ip': '100.125.201.100',
        'role': 'REDUNDANT_1'
    },
    'sah6': {
        'tailscale_ip': '100.92.174.24',
        'role': 'REDUNDANT_2'
    },
    'openclaw': {
        'tailscale_ip': '100.113.1.85',
        'role': 'BACKUP'
    }
}

# ============================================================
# SSH TUNNEL MANAGER
# ============================================================

class SSHTunnelManager:
    def __init__(self):
        self.ssh_client = None
        self.connected = False
        self.last_connect_time = None
        self.reconnect_count = 0
        
    def connect(self) -> bool:
        try:
            private_key = paramiko.Ed25519Key.from_private_key_file(
                CREDENTIALS['ssh_key_path']
            )
            
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.ssh_client.connect(
                CREDENTIALS['upcloud_public_ip'],
                port=22,
                username=CREDENTIALS['ssh_user'],
                pkey=private_key,
                timeout=15
            )
            
            self.connected = True
            self.last_connect_time = datetime.now()
            self.reconnect_count = 0
            logger.info("✅ SSH tunnel established to UpCloud")
            return True
            
        except Exception as e:
            logger.error(f"SSH connection failed: {e}")
            self.connected = False
            return False
    
    def execute(self, command: str, timeout: int = 60) -> Dict:
        """Execute command via SSH with fallback to Execute API"""
        if self.connected and self.ssh_client:
            try:
                stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=timeout)
                return {
                    'returncode': stdout.channel.recv_exit_status(),
                    'stdout': stdout.read().decode(),
                    'stderr': stderr.read().decode(),
                    'success': True,
                    'via': 'ssh'
                }
            except Exception as e:
                logger.warning(f"SSH exec failed, trying API fallback: {e}")
                self.connected = False
        
        # Fallback to Execute API
        return self._execute_via_api(command)
    
    def _execute_via_api(self, command: str) -> Dict:
        """Fallback to Execute API"""
        try:
            url = f"http://{CREDENTIALS['upcloud_public_ip']}:{CREDENTIALS['execute_api_port']}/execute"
            headers = {
                'X-Auth-Token': CREDENTIALS['auth_token'],
                'Content-Type': 'application/json'
            }
            data = {'command': command}
            
            r = requests.post(url, headers=headers, json=data, timeout=30)
            if r.status_code == 200:
                result = r.json()
                result['via'] = 'api'
                return result
            return {'success': False, 'error': f"API error: {r.status_code}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def keepalive(self):
        """Send keepalive to maintain connection"""
        if self.connected and self.ssh_client:
            try:
                transport = self.ssh_client.get_transport()
                if transport:
                    transport.send_ignore()
            except:
                self.connected = False
    
    def reconnect(self) -> bool:
        """Attempt to reconnect"""
        self.reconnect_count += 1
        if self.ssh_client:
            try:
                self.ssh_client.close()
            except:
                pass
        return self.connect()

# ============================================================
# LOCAL API SERVER
# ============================================================

class LocalAPIServer:
    def __init__(self, tunnel_manager: SSHTunnelManager):
        self.tunnel = tunnel_manager
        self.app = Flask(__name__)
        self.running = False
        self._setup_routes()
    
    def _setup_routes(self):
        @self.app.route('/health')
        def health():
            return jsonify({
                'status': 'healthy',
                'ssh_connected': self.tunnel.connected,
                'last_connect': str(self.tunnel.last_connect_time),
                'reconnect_count': self.tunnel.reconnect_count,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/execute', methods=['POST'])
        def execute():
            data = request.get_json()
            command = data.get('command')
            if not command:
                return jsonify({'error': 'No command provided'}), 400
            
            result = self.tunnel.execute(command)
            return jsonify(result)
        
        @self.app.route('/mesh/status')
        def mesh_status():
            # Check all mesh nodes via UpCloud
            result = self.tunnel.execute('tailscale status')
            return jsonify({
                'raw_output': result.get('stdout', ''),
                'nodes': MESH_NODES,
                'via': result.get('via', 'unknown')
            })
        
        @self.app.route('/hermes/start', methods=['POST'])
        def start_hermes():
            result = self.tunnel.execute('systemctl start hermes && systemctl status hermes --no-pager')
            return jsonify(result)
        
        @self.app.route('/hermes/stop', methods=['POST'])
        def stop_hermes():
            result = self.tunnel.execute('systemctl stop hermes')
            return jsonify(result)
        
        @self.app.route('/hermes/logs')
        def hermes_logs():
            result = self.tunnel.execute('tail -50 /opt/hermes/logs/hermes.log 2>/dev/null || journalctl -u hermes -n 50 --no-pager')
            return jsonify(result)
        
        @self.app.route('/sync/memory', methods=['POST'])
        def sync_memory():
            """Sync memory with UpCloud"""
            data = request.get_json()
            memory_data = data.get('memory', {})
            
            # Save locally
            memory_file = Path('/home/z/my-project/kiswarm_data/memory/glm_memory.json')
            memory_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(memory_file, 'w') as f:
                json.dump(memory_data, f, indent=2)
            
            # Sync to UpCloud
            memory_json = json.dumps(memory_data)
            result = self.tunnel.execute(
                f"mkdir -p /opt/hermes/memory && echo '{memory_json}' > /opt/hermes/memory/glm_sync.json"
            )
            
            return jsonify({
                'local_saved': True,
                'remote_sync': result.get('success', False)
            })
    
    def run(self, port: int = 5557):
        self.running = True
        logger.info(f"🌐 Local API server starting on port {port}")
        self.app.run(host='0.0.0.0', port=port, threaded=True)

# ============================================================
# TELEGRAM NOTIFIER
# ============================================================

class TelegramNotifier:
    def __init__(self):
        self.token = CREDENTIALS['telegram_token']
        self.chat_id = CREDENTIALS['admin_chat_id']
        self.api_url = f"https://api.telegram.org/bot{self.token}"
    
    def send(self, message: str) -> bool:
        try:
            r = requests.post(
                f"{self.api_url}/sendMessage",
                json={'chat_id': self.chat_id, 'text': message[:4096]},
                timeout=30
            )
            return r.status_code == 200
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            return False
    
    def notify_startup(self):
        self.send(f"""🌀 GLM PERSISTENT TUNNEL ONLINE
============================
Time: {datetime.now().isoformat()}
Status: Connected to UpCloud Master
Local API: Port 5557
Mesh Nodes: {len(MESH_NODES)} registered""")

# ============================================================
# MAIN SERVICE
# ============================================================

class GLMPersistentTunnel:
    def __init__(self):
        self.tunnel = SSHTunnelManager()
        self.api = LocalAPIServer(self.tunnel)
        self.telegram = TelegramNotifier()
        self.running = False
        
    def start(self):
        logger.info("🌀 ==========================================")
        logger.info("🌀 GLM PERSISTENT TUNNEL v2.0")
        logger.info("🌀 ==========================================")
        
        # Connect SSH
        if self.tunnel.connect():
            logger.info("✅ SSH tunnel ready")
        else:
            logger.warning("⚠️ SSH failed, using API fallback")
        
        # Notify
        self.telegram.notify_startup()
        
        # Start API server in background
        api_thread = threading.Thread(
            target=self.api.run,
            args=(CREDENTIALS['local_api_port'],),
            daemon=True
        )
        api_thread.start()
        
        # Main loop
        self.running = True
        while self.running:
            try:
                # Keepalive every 30 seconds
                time.sleep(30)
                
                if self.tunnel.connected:
                    self.tunnel.keepalive()
                else:
                    # Try to reconnect
                    logger.info("Attempting reconnect...")
                    self.tunnel.reconnect()
                    
            except KeyboardInterrupt:
                self.running = False
                logger.info("Shutting down...")

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    service = GLMPersistentTunnel()
    try:
        service.start()
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
