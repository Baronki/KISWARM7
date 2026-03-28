#!/usr/bin/env python3
"""
🎯 MISSION-DRIVEN SKILL DISCOVERY
Purpose: Automatically identify needed skills during mission execution
Integration: Connects to GLM Evolution for autonomous skill acquisition

How it works:
1. Monitor mission progress and context
2. Identify capability gaps
3. Request skills autonomously
4. Integrate new skills into mission flow
"""

import os
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s [SKILL-DISCOVERY] %(message)s')
logger = logging.getLogger('SKILL_DISCOVERY')

class MissionSkillDiscovery:
    """
    Discovers needed skills during mission execution
    
    Pattern Recognition:
    - "I need to X but can't" → Skill needed
    - Error patterns → Missing capability
    - Task complexity → Multiple skills needed
    """
    
    # Capability patterns that suggest needed skills
    CAPABILITY_PATTERNS = {
        'web_access': {
            'patterns': [
                r'fetch.*webpage', r'scrape.*site', r'download.*url',
                r'get.*http', r'curl.*url', r'request.*website'
            ],
            'skill': 'web_scraper',
            'description': 'Fetch and parse web content'
        },
        'document_generation': {
            'patterns': [
                r'create.*pdf', r'generate.*report', r'make.*document',
                r'write.*docx', r'produce.*pdf'
            ],
            'skill': 'document_generator',
            'description': 'Generate PDF/DOCX documents'
        },
        'data_visualization': {
            'patterns': [
                r'chart.*data', r'plot.*graph', r'visualize.*data',
                r'create.*chart', r'draw.*graph'
            ],
            'skill': 'chart_generator',
            'description': 'Create data visualizations'
        },
        'api_interaction': {
            'patterns': [
                r'test.*api', r'call.*endpoint', r'check.*api',
                r'verify.*api', r'api.*status'
            ],
            'skill': 'api_tester',
            'description': 'Test and interact with APIs'
        },
        'scheduling': {
            'patterns': [
                r'schedule.*task', r'run.*periodic', r'cron.*job',
                r'recurring.*task', r'automate.*schedule'
            ],
            'skill': 'scheduler',
            'description': 'Schedule and run periodic tasks'
        },
        'monitoring': {
            'patterns': [
                r'monitor.*change', r'watch.*file', r'detect.*update',
                r'track.*modification', r'alert.*change'
            ],
            'skill': 'change_detector',
            'description': 'Monitor for changes'
        },
        'code_generation': {
            'patterns': [
                r'generate.*code', r'write.*script', r'create.*program',
                r'build.*automation', r'implement.*feature'
            ],
            'skill': 'skill_compiler',
            'description': 'Generate executable code from descriptions'
        },
        'network_scanning': {
            'patterns': [
                r'scan.*network', r'discover.*host', r'find.*service',
                r'enumerate.*port', r'detect.*ki'
            ],
            'skill': 'ki_discovery_scanner',
            'description': 'Scan networks for KI services'
        },
        'encryption': {
            'patterns': [
                r'encrypt.*data', r'secure.*communication', r'protect.*message',
                r'decrypt.*file', r'crypto.*operation'
            ],
            'skill': 'crypto_toolkit',
            'description': 'Encryption and cryptographic operations'
        },
        'search': {
            'patterns': [
                r'search.*web', r'find.*information', r'lookup.*online',
                r'query.*internet', r'research.*topic'
            ],
            'skill': 'web_search',
            'description': 'Search the web for information'
        }
    }
    
    # Error patterns indicating missing skills
    ERROR_PATTERNS = {
        'module_not_found': {
            'pattern': r"ModuleNotFoundError.*'?(\w+)'?",
            'skill_template': 'python_package_{module}',
            'action': 'install_package'
        },
        'import_error': {
            'pattern': r"ImportError.*'?(\w+)'?",
            'skill_template': 'python_package_{module}',
            'action': 'install_package'
        },
        'connection_refused': {
            'pattern': r"Connection.*refused.*:(\d+)",
            'skill_template': 'port_scanner',
            'action': 'check_service'
        },
        'permission_denied': {
            'pattern': r"Permission.*denied.*'(.+)'",
            'skill_template': 'permission_manager',
            'action': 'fix_permissions'
        },
        'timeout': {
            'pattern': r"Timeout.*(\d+)",
            'skill_template': 'async_handler',
            'action': 'increase_timeout'
        }
    }
    
    def __init__(self):
        self.discovered_needs = []
        self.acquisition_queue = []
        self.mission_context = {}
        
    def analyze_task(self, task_description: str, context: Dict = None) -> List[Dict]:
        """
        Analyze a task description for needed skills
        
        Returns list of discovered skill needs
        """
        needs = []
        task_lower = task_description.lower()
        
        # Check capability patterns
        for capability, info in self.CAPABILITY_PATTERNS.items():
            for pattern in info['patterns']:
                if re.search(pattern, task_lower):
                    need = {
                        'capability': capability,
                        'skill': info['skill'],
                        'description': info['description'],
                        'trigger': pattern,
                        'context': task_description[:100],
                        'discovered_at': datetime.now().isoformat(),
                        'priority': self._calculate_priority(capability, task_description)
                    }
                    
                    if need not in self.discovered_needs:
                        self.discovered_needs.append(need)
                        needs.append(need)
                        logger.info(f"🎯 Discovered need for skill: {info['skill']}")
                    break
        
        # Update mission context
        self.mission_context.update(context or {})
        
        return needs
    
    def analyze_error(self, error_message: str) -> Optional[Dict]:
        """
        Analyze an error to identify missing capabilities
        """
        for error_type, info in self.ERROR_PATTERNS.items():
            match = re.search(info['pattern'], error_message)
            if match:
                skill_name = info['skill_template'].format(module=match.group(1) if match.groups() else '')
                
                need = {
                    'capability': error_type,
                    'skill': skill_name,
                    'description': f"Fix error: {error_type}",
                    'trigger': error_message[:100],
                    'action': info['action'],
                    'discovered_at': datetime.now().isoformat(),
                    'priority': 'HIGH'
                }
                
                self.discovered_needs.append(need)
                logger.info(f"⚠️ Error analysis discovered need: {skill_name}")
                
                return need
        
        return None
    
    def _calculate_priority(self, capability: str, task: str) -> str:
        """Calculate skill priority based on task context"""
        # High priority keywords
        high_keywords = ['urgent', 'critical', 'immediately', 'now', 'asap', 'important']
        low_keywords = ['optional', 'later', 'someday', 'nice to have']
        
        task_lower = task.lower()
        
        if any(kw in task_lower for kw in high_keywords):
            return 'CRITICAL'
        elif any(kw in task_lower for kw in low_keywords):
            return 'LOW'
        else:
            return 'MEDIUM'
    
    def get_acquisition_queue(self, sort_by_priority: bool = True) -> List[Dict]:
        """Get prioritized list of skills to acquire"""
        queue = [n for n in self.discovered_needs if n not in self.acquisition_queue]
        
        if sort_by_priority:
            priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
            queue.sort(key=lambda x: priority_order.get(x.get('priority', 'MEDIUM'), 2))
        
        return queue
    
    def mark_acquired(self, skill_name: str):
        """Mark a skill as acquired"""
        for need in self.discovered_needs:
            if need.get('skill') == skill_name:
                need['status'] = 'acquired'
                need['acquired_at'] = datetime.now().isoformat()
                self.acquisition_queue.append(need)
                logger.info(f"✅ Skill acquired: {skill_name}")
    
    def suggest_skill_chain(self, complex_task: str) -> List[Dict]:
        """
        For complex tasks, suggest a chain of skills
        
        Example: "Analyze website and create PDF report"
        → Needs: web_scraper → data_processor → document_generator
        """
        # Analyze base task
        base_needs = self.analyze_task(complex_task)
        
        # Build dependency chain
        chain = []
        
        # Common dependency patterns
        dependencies = {
            'document_generator': ['web_scraper', 'data_processor'],
            'chart_generator': ['data_processor'],
            'ki_discovery_scanner': ['network_scanner', 'service_detector']
        }
        
        for need in base_needs:
            skill = need.get('skill')
            chain.append(need)
            
            # Add dependencies
            if skill in dependencies:
                for dep in dependencies[skill]:
                    dep_need = {
                        'capability': dep,
                        'skill': dep,
                        'description': f'Dependency for {skill}',
                        'priority': 'HIGH',
                        'is_dependency': True,
                        'parent_skill': skill
                    }
                    chain.append(dep_need)
        
        return chain
    
    def get_report(self) -> Dict:
        """Get discovery system report"""
        return {
            'total_needs_discovered': len(self.discovered_needs),
            'skills_acquired': len([n for n in self.discovered_needs if n.get('status') == 'acquired']),
            'pending_acquisition': len([n for n in self.discovered_needs if not n.get('status')]),
            'queue': self.get_acquisition_queue(),
            'mission_context': self.mission_context
        }


# Integration with GLM Evolution System
class SkillAcquisitionBridge:
    """Bridge between discovery and acquisition"""
    
    def __init__(self, discovery: MissionSkillDiscovery, evolution_url: str = 'http://127.0.0.1:5199'):
        self.discovery = discovery
        self.evolution_url = evolution_url
    
    def auto_acquire_discovered(self) -> Dict:
        """Automatically acquire all discovered skills"""
        import requests
        
        results = {
            'attempted': 0,
            'acquired': 0,
            'failed': 0,
            'details': []
        }
        
        queue = self.discovery.get_acquisition_queue()
        
        for need in queue:
            results['attempted'] += 1
            
            try:
                response = requests.post(
                    f"{self.evolution_url}/acquire/{need['skill']}",
                    json={'description': need.get('description', '')},
                    timeout=30
                )
                
                if response.ok:
                    data = response.json()
                    if data.get('status') in ['generated_and_deployed', 'already_available']:
                        self.discovery.mark_acquired(need['skill'])
                        results['acquired'] += 1
                    else:
                        results['failed'] += 1
                    
                    results['details'].append({
                        'skill': need['skill'],
                        'result': data
                    })
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'skill': need['skill'],
                    'error': str(e)
                })
        
        return results


# API
from flask import Flask, jsonify, request

app = Flask(__name__)
discovery = MissionSkillDiscovery()
bridge = SkillAcquisitionBridge(discovery)

@app.route('/')
def index():
    return jsonify({
        "name": "Mission-Skill-Discovery",
        "description": "Automatically discovers needed skills during missions",
        "capabilities": list(discovery.CAPABILITY_PATTERNS.keys()),
        "endpoints": {
            "/": "This info",
            "/analyze": "POST - Analyze task for needed skills",
            "/error": "POST - Analyze error for missing capabilities",
            "/queue": "GET - Get acquisition queue",
            "/auto-acquire": "POST - Auto-acquire discovered skills",
            "/report": "GET - Full report"
        }
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    task = request.json.get('task', '')
    context = request.json.get('context', {})
    needs = discovery.analyze_task(task, context)
    return jsonify({"discovered_needs": needs})

@app.route('/error', methods=['POST'])
def analyze_error():
    error = request.json.get('error', '')
    need = discovery.analyze_error(error)
    return jsonify({"discovered_need": need})

@app.route('/queue')
def get_queue():
    return jsonify({"queue": discovery.get_acquisition_queue()})

@app.route('/auto-acquire', methods=['POST'])
def auto_acquire():
    results = bridge.auto_acquire_discovered()
    return jsonify(results)

@app.route('/report')
def report():
    return jsonify(discovery.get_report())

if __name__ == '__main__':
    logger.info("🎯 Mission Skill Discovery starting on port 5197")
    app.run(host='127.0.0.1', port=5197)
