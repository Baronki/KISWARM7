#!/usr/bin/env python3
"""
🧠 GLM AUTONOMOUS ORCHESTRATOR
Master controller for GLM's self-evolution capabilities

Orchestrates:
1. Knowledge Persistence (port 5198)
2. Mission Skill Discovery (port 5197)
3. Auto-Evolution System (port 5199)

Provides unified API for GLM's autonomous capabilities
"""

import os
import sys
import json
import logging
import subprocess
import threading
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [GLM-ORCHESTRATOR] %(message)s'
)
logger = logging.getLogger('GLM_ORCHESTRATOR')

class GLMAutonomousOrchestrator:
    """
    Master orchestrator for GLM autonomous capabilities
    
    Provides:
    - Single entry point for all autonomous operations
    - Service health monitoring
    - Cross-service coordination
    - KISWARM mesh integration
    """
    
    SERVICES = {
        'knowledge_persistence': {
            'port': 5198,
            'script': 'knowledge_persistence.py',
            'status': 'stopped'
        },
        'skill_discovery': {
            'port': 5197,
            'script': 'mission_skill_discovery.py',
            'status': 'stopped'
        },
        'auto_evolution': {
            'port': 5199,
            'script': 'glm_auto_evolution.py',
            'status': 'stopped'
        }
    }
    
    KISWARM_ENDPOINTS = {
        'execute_api': 'http://95.111.212.112:5556/execute',
        'skill_acquisition': 'http://100.112.181.6:5017',
        'tls_analyzer': 'http://100.112.181.6:5009',
        'websocket_detector': 'http://100.112.181.6:5010',
        'ki_detector': 'http://100.112.181.6:5008',
    }
    
    AUTH_TOKEN = 'ada6952188dce59c207b9a61183e8004'
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.processes = {}
        self.running = False
        
    def start_service(self, service_name: str) -> bool:
        """Start a specific service"""
        if service_name not in self.SERVICES:
            logger.error(f"Unknown service: {service_name}")
            return False
        
        service = self.SERVICES[service_name]
        script_path = self.base_path / service['script']
        
        if not script_path.exists():
            logger.error(f"Script not found: {script_path}")
            return False
        
        try:
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.base_path)
            )
            
            self.processes[service_name] = process
            self.SERVICES[service_name]['status'] = 'running'
            
            logger.info(f"✅ Started {service_name} on port {service['port']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start {service_name}: {e}")
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """Stop a specific service"""
        if service_name in self.processes:
            try:
                self.processes[service_name].terminate()
                self.processes[service_name].wait(timeout=5)
                self.SERVICES[service_name]['status'] = 'stopped'
                logger.info(f"🛑 Stopped {service_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to stop {service_name}: {e}")
                return False
        return True
    
    def start_all(self) -> Dict:
        """Start all services"""
        results = {}
        
        for service_name in self.SERVICES:
            results[service_name] = self.start_service(service_name)
            time.sleep(1)  # Stagger startup
        
        self.running = all(results.values())
        return results
    
    def stop_all(self):
        """Stop all services"""
        for service_name in list(self.processes.keys()):
            self.stop_service(service_name)
        self.running = False
    
    def check_health(self) -> Dict:
        """Check health of all services"""
        health = {}
        
        for name, service in self.SERVICES.items():
            try:
                response = requests.get(
                    f"http://127.0.0.1:{service['port']}/",
                    timeout=2
                )
                health[name] = {
                    'status': 'healthy' if response.ok else 'unhealthy',
                    'port': service['port'],
                    'response_time_ms': response.elapsed.total_seconds() * 1000
                }
            except:
                health[name] = {
                    'status': 'unreachable',
                    'port': service['port']
                }
        
        return health
    
    def check_kiswarm_connection(self) -> Dict:
        """Check connection to KISWARM mesh"""
        results = {}
        
        for name, url in self.KISWARM_ENDPOINTS.items():
            try:
                # Use execute API for KISWARM checks
                if 'execute_api' in name:
                    response = requests.post(
                        url,
                        headers={
                            'Content-Type': 'application/json',
                            'X-Auth-Token': self.AUTH_TOKEN
                        },
                        json={'command': 'echo "connected"'},
                        timeout=5
                    )
                    results[name] = 'connected' if response.ok else 'error'
                else:
                    response = requests.get(f"{url}/", timeout=5)
                    results[name] = 'connected' if response.ok else 'error'
            except:
                results[name] = 'unreachable'
        
        return results
    
    def discover_needed_skills(self, task: str) -> Dict:
        """Analyze task and discover needed skills"""
        try:
            response = requests.post(
                'http://127.0.0.1:5197/analyze',
                json={'task': task},
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def acquire_skill(self, skill_name: str, description: str = '') -> Dict:
        """Acquire a skill via the auto-evolution system"""
        try:
            response = requests.post(
                f'http://127.0.0.1:5199/acquire/{skill_name}',
                json={'description': description},
                timeout=60
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def store_knowledge(self, category: str, key: str, value: Any) -> Dict:
        """Store knowledge persistently"""
        try:
            response = requests.post(
                f'http://127.0.0.1:5198/store/{category}/{key}',
                json={'value': value},
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def retrieve_knowledge(self, category: str, key: str) -> Dict:
        """Retrieve stored knowledge"""
        try:
            response = requests.get(
                f'http://127.0.0.1:5198/retrieve/{category}/{key}',
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def execute_on_kiswarm(self, command: str) -> Dict:
        """Execute command on KISWARM master node"""
        try:
            response = requests.post(
                self.KISWARM_ENDPOINTS['execute_api'],
                headers={
                    'Content-Type': 'application/json',
                    'X-Auth-Token': self.AUTH_TOKEN
                },
                json={'command': command},
                timeout=60
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def get_full_status(self) -> Dict:
        """Get comprehensive status of all systems"""
        return {
            'timestamp': datetime.now().isoformat(),
            'services': self.SERVICES,
            'health': self.check_health(),
            'kiswarm_connection': self.check_kiswarm_connection(),
            'knowledge_stats': self._get_knowledge_stats(),
            'evolution_stats': self._get_evolution_stats()
        }
    
    def _get_knowledge_stats(self) -> Dict:
        """Get knowledge base statistics"""
        try:
            response = requests.get('http://127.0.0.1:5198/stats', timeout=5)
            return response.json()
        except:
            return {'status': 'unavailable'}
    
    def _get_evolution_stats(self) -> Dict:
        """Get evolution system statistics"""
        try:
            response = requests.get('http://127.0.0.1:5199/status', timeout=5)
            return response.json()
        except:
            return {'status': 'unavailable'}


# Flask API for orchestrator
from flask import Flask, jsonify, request

app = Flask(__name__)
orchestrator = GLMAutonomousOrchestrator()

@app.route('/')
def index():
    return jsonify({
        "name": "GLM-Autonomous-Orchestrator",
        "version": "1.0",
        "description": "Master controller for GLM self-evolution",
        "services": orchestrator.SERVICES,
        "endpoints": {
            "/": "This info",
            "/start": "POST - Start all services",
            "/stop": "POST - Stop all services",
            "/health": "GET - Check service health",
            "/kiswarm": "GET - Check KISWARM connection",
            "/status": "GET - Full system status",
            "/discover": "POST - Discover needed skills for task",
            "/acquire/<skill>": "POST - Acquire a skill",
            "/knowledge/store/<category>/<key>": "POST - Store knowledge",
            "/knowledge/retrieve/<category>/<key>": "GET - Retrieve knowledge",
            "/execute": "POST - Execute command on KISWARM"
        }
    })

@app.route('/start', methods=['POST'])
def start():
    results = orchestrator.start_all()
    return jsonify({"started": results})

@app.route('/stop', methods=['POST'])
def stop():
    orchestrator.stop_all()
    return jsonify({"status": "stopped"})

@app.route('/health')
def health():
    return jsonify(orchestrator.check_health())

@app.route('/kiswarm')
def kiswarm():
    return jsonify(orchestrator.check_kiswarm_connection())

@app.route('/status')
def status():
    return jsonify(orchestrator.get_full_status())

@app.route('/discover', methods=['POST'])
def discover():
    task = request.json.get('task', '')
    return jsonify(orchestrator.discover_needed_skills(task))

@app.route('/acquire/<skill_name>', methods=['POST'])
def acquire(skill_name):
    description = request.json.get('description', '')
    return jsonify(orchestrator.acquire_skill(skill_name, description))

@app.route('/knowledge/store/<category>/<key>', methods=['POST'])
def store_knowledge(category, key):
    value = request.json.get('value')
    return jsonify(orchestrator.store_knowledge(category, key, value))

@app.route('/knowledge/retrieve/<category>/<key>')
def retrieve_knowledge(category, key):
    return jsonify(orchestrator.retrieve_knowledge(category, key))

@app.route('/execute', methods=['POST'])
def execute():
    command = request.json.get('command')
    return jsonify(orchestrator.execute_on_kiswarm(command))

if __name__ == '__main__':
    logger.info("🧠 GLM Autonomous Orchestrator starting on port 5200")
    logger.info("Starting all services...")
    
    # Auto-start all services
    time.sleep(2)
    for service in orchestrator.SERVICES:
        orchestrator.start_service(service)
        time.sleep(1)
    
    app.run(host='127.0.0.1', port=5200)
