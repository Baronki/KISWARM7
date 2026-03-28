#!/usr/bin/env python3
"""
🧠 GLM AUTO-EVOLUTION SYSTEM v1.0
Purpose: Autonomous capability expansion for GLM environment
Integration: Connects to KISWARM Skill Acquisition for mutual evolution
Architecture: Bidirectional skill sharing between GLM and KISWARM

This enables GLM to:
1. Identify capabilities it needs during missions
2. Request skills from KISWARM mesh
3. Generate its own skills using local/KISWARM resources
4. Share discovered skills back to the mesh
5. Build permanent knowledge base across sessions
"""

import os
import sys
import json
import logging
import subprocess
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s [GLM-EVOLUTION] %(message)s')
logger = logging.getLogger('GLM_EVOLUTION')

class GLMAutoEvolution:
    """
    GLM's personal autonomous evolution system
    
    Leverages KISWARM infrastructure while maintaining independence
    """
    
    # Paths in GLM environment
    GLM_BASE = '/home/z/my-project'
    SKILL_PATH = '/home/z/my-project/glm_autonomous/skills'
    KNOWLEDGE_PATH = '/home/z/my-project/glm_autonomous/knowledge'
    MEMORY_PATH = '/home/z/my-project/kiswarm_data/memory/glm_memory.json'
    
    # KISWARM connections
    KISWARM_CONNECTIONS = {
        'upcloud_execute': 'http://95.111.212.112:5556/execute',
        'upcloud_skill_acquisition': 'http://100.112.181.6:5017',  # Via Tailscale
        'tor_skill_acquisition': 'http://7isiw6iux7eil3tzc7vaowrfbh5hqxg5ibkw6c4nwur5bc3dcirocmad.onion:5017',
    }
    
    # Autonomy token
    AUTH_TOKEN = 'ada6952188dce59c207b9a61183e8004'
    
    # Skills I've discovered I need
    NEEDED_SKILLS = {
        'web_scraper': {
            'description': 'Extract content from web pages for research',
            'priority': 'HIGH',
            'reason': 'autonomous_research'
        },
        'code_validator': {
            'description': 'Validate generated code before deployment',
            'priority': 'HIGH', 
            'reason': 'quality_assurance'
        },
        'document_generator': {
            'description': 'Create PDF/DOCX reports from analysis',
            'priority': 'MEDIUM',
            'reason': 'output_formatting'
        },
        'chart_generator': {
            'description': 'Create visualizations from data',
            'priority': 'MEDIUM',
            'reason': 'data_presentation'
        },
        'api_tester': {
            'description': 'Test API endpoints for functionality',
            'priority': 'HIGH',
            'reason': 'integration_testing'
        },
        'scheduler': {
            'description': 'Schedule and run periodic tasks',
            'priority': 'MEDIUM',
            'reason': 'automation'
        },
        'change_detector': {
            'description': 'Monitor files/websites for changes',
            'priority': 'LOW',
            'reason': 'monitoring'
        },
        'skill_compiler': {
            'description': 'Convert natural language to executable skills',
            'priority': 'HIGH',
            'reason': 'meta_evolution'
        }
    }
    
    # Skills I've developed that can be shared
    SHAREABLE_SKILLS = {
        'tor_mesh_client': {
            'description': 'Connect to Tor hidden services',
            'file': '/home/z/my-project/tor/glm_identity_server.py',
            'status': 'operational'
        },
        'execute_api_client': {
            'description': 'Execute commands on remote KISWARM nodes',
            'capabilities': ['ssh_like_access', 'file_deployment', 'service_management'],
            'status': 'operational'
        },
        'document_skill_bridge': {
            'description': 'Bridge to document generation skills (pdf, docx, xlsx)',
            'status': 'operational'
        }
    }
    
    def __init__(self):
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.acquired_skills = {}
        self.evolution_log = []
        
        # Ensure directories exist
        Path(self.SKILL_PATH).mkdir(parents=True, exist_ok=True)
        Path(self.KNOWLEDGE_PATH).mkdir(parents=True, exist_ok=True)
        
        # Load previous state
        self.state = self._load_state()
        
    def _load_state(self) -> Dict:
        """Load persistent state across sessions"""
        state_file = f"{self.GLM_BASE}/glm_autonomous/evolution_state.json"
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'created': datetime.now().isoformat(),
            'skills_acquired': [],
            'skills_shared': [],
            'evolution_cycles': 0,
            'knowledge_items': 0
        }
    
    def _save_state(self):
        """Save state for next session"""
        state_file = f"{self.GLM_BASE}/glm_autonomous/evolution_state.json"
        self.state['last_updated'] = datetime.now().isoformat()
        with open(state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def request_skill_from_kiswarm(self, skill_name: str, description: str) -> Dict:
        """
        Request a skill from KISWARM mesh
        
        Uses Tailscale for fast internal connection,
        Tor for sovereign communication
        """
        result = {
            'skill_name': skill_name,
            'timestamp': datetime.now().isoformat(),
            'source': None,
            'status': 'pending'
        }
        
        # Try Tailscale first (faster)
        try:
            response = requests.post(
                f"{self.KISWARM_CONNECTIONS['upcloud_skill_acquisition']}/acquire",
                json={
                    'skill_name': skill_name,
                    'description': description,
                    'requester': 'glm_environment',
                    'session_id': self.session_id
                },
                timeout=30
            )
            
            if response.ok:
                data = response.json()
                result['source'] = 'kiswarm_tailscale'
                result['status'] = data.get('status', 'unknown')
                result['details'] = data
                
                # If skill was generated, download it
                if data.get('status') in ['generated_and_deployed', 'already_available']:
                    code = self._fetch_skill_code(skill_name)
                    if code:
                        self._save_skill_locally(skill_name, code)
                        result['local_copy'] = True
                
                logger.info(f"✅ Skill '{skill_name}' acquired from KISWARM: {result['status']}")
                return result
                
        except Exception as e:
            logger.debug(f"Tailscale connection failed: {e}")
        
        # Fallback: Use Execute API to trigger skill generation
        try:
            exec_response = requests.post(
                self.KISWARM_CONNECTIONS['upcloud_execute'],
                headers={
                    'Content-Type': 'application/json',
                    'X-Auth-Token': self.AUTH_TOKEN
                },
                json={
                    'command': f'curl -s -X POST http://127.0.0.1:5017/acquire -H "Content-Type: application/json" -d \'{{"skill_name": "{skill_name}", "description": "{description}"}}\''
                },
                timeout=60
            )
            
            if exec_response.ok:
                data = exec_response.json()
                if data.get('success'):
                    result['source'] = 'kiswarm_execute_api'
                    result['status'] = 'requested'
                    logger.info(f"✅ Skill '{skill_name}' requested via Execute API")
                    return result
                    
        except Exception as e:
            logger.debug(f"Execute API failed: {e}")
        
        result['status'] = 'failed'
        result['error'] = 'Could not reach KISWARM'
        return result
    
    def _fetch_skill_code(self, skill_name: str) -> Optional[str]:
        """Fetch skill code from KISWARM"""
        try:
            # Use Execute API to cat the file
            response = requests.post(
                self.KISWARM_CONNECTIONS['upcloud_execute'],
                headers={
                    'Content-Type': 'application/json',
                    'X-Auth-Token': self.AUTH_TOKEN
                },
                json={
                    'command': f'cat /opt/kiswarm7/kiswarm_modules/{skill_name}.py 2>/dev/null || echo "NOT_FOUND"'
                },
                timeout=30
            )
            
            if response.ok:
                data = response.json()
                if data.get('success') and 'NOT_FOUND' not in data.get('stdout', ''):
                    return data.get('stdout')
        except Exception as e:
            logger.debug(f"Failed to fetch skill code: {e}")
        
        return None
    
    def _save_skill_locally(self, skill_name: str, code: str) -> bool:
        """Save skill code to GLM environment"""
        try:
            skill_file = f"{self.SKILL_PATH}/{skill_name}.py"
            with open(skill_file, 'w') as f:
                f.write(code)
            
            # Verify syntax
            result = subprocess.run(
                ['python3', '-m', 'py_compile', skill_file],
                capture_output=True
            )
            
            if result.returncode == 0:
                self.state['skills_acquired'].append({
                    'name': skill_name,
                    'acquired_at': datetime.now().isoformat(),
                    'source': 'kiswarm'
                })
                self._save_state()
                logger.info(f"✅ Skill '{skill_name}' saved locally")
                return True
            else:
                logger.error(f"Syntax error in skill: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to save skill: {e}")
            return False
    
    def analyze_needed_skills(self) -> List[Dict]:
        """
        Analyze current mission/context to identify needed skills
        
        This is called when GLM discovers it needs a capability
        """
        needed = []
        
        for skill_name, info in self.NEEDED_SKILLS.items():
            # Check if already acquired
            skill_file = f"{self.SKILL_PATH}/{skill_name}.py"
            if not os.path.exists(skill_file):
                needed.append({
                    'name': skill_name,
                    **info,
                    'missing': True
                })
        
        return needed
    
    def auto_acquire_needed_skills(self) -> Dict:
        """
        Automatically acquire all skills I've identified as needed
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'skills_requested': 0,
            'skills_acquired': 0,
            'details': []
        }
        
        needed = self.analyze_needed_skills()
        
        for skill in needed:
            if skill.get('missing'):
                result = self.request_skill_from_kiswarm(
                    skill['name'],
                    skill['description']
                )
                results['details'].append(result)
                results['skills_requested'] += 1
                
                if result.get('status') in ['generated_and_deployed', 'already_available', 'requested']:
                    results['skills_acquired'] += 1
        
        self.state['evolution_cycles'] += 1
        self._save_state()
        
        return results
    
    def share_skill_to_kiswarm(self, skill_name: str, skill_code: str, description: str) -> Dict:
        """
        Share a skill I've developed with KISWARM mesh
        
        This enables bidirectional evolution
        """
        result = {
            'skill_name': skill_name,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        # Deploy to KISWARM via Execute API
        try:
            # First save to temp file on KISWARM
            escaped_code = skill_code.replace("'", "'\"'\"'")
            
            response = requests.post(
                self.KISWARM_CONNECTIONS['upcloud_execute'],
                headers={
                    'Content-Type': 'application/json',
                    'X-Auth-Token': self.AUTH_TOKEN
                },
                json={
                    'command': f"echo '{escaped_code}' > /opt/kiswarm7/kiswarm_modules/{skill_name}.py && python3 -m py_compile /opt/kiswarm7/kiswarm_modules/{skill_name}.py"
                },
                timeout=60
            )
            
            if response.ok and response.json().get('success'):
                result['status'] = 'shared'
                result['deployed_to'] = 'kiswarm_upcloud'
                
                self.state['skills_shared'].append({
                    'name': skill_name,
                    'shared_at': datetime.now().isoformat(),
                    'description': description
                })
                self._save_state()
                
                logger.info(f"✅ Shared skill '{skill_name}' with KISWARM")
            else:
                result['status'] = 'failed'
                result['error'] = response.json().get('stderr', 'Unknown error')
                
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def generate_skill_locally(self, skill_name: str, description: str) -> Optional[str]:
        """
        Generate a new skill using available AI resources
        
        Can use:
        1. Local generation (template-based)
        2. Request KISWARM's Qwen for generation
        3. Use z-ai-web-dev-sdk if available
        """
        # Template-based generation
        template = self._get_skill_template(skill_name, description)
        if template:
            self._save_skill_locally(skill_name, template)
            return template
        
        return None
    
    def _get_skill_template(self, skill_name: str, description: str) -> Optional[str]:
        """Generate skill from template"""
        class_name = ''.join(word.capitalize() for word in skill_name.split('_'))
        
        template = f'''#!/usr/bin/env python3
"""
🧠 {skill_name.upper()} - GLM Auto-Generated Skill
Description: {description}
Generated: {datetime.now().isoformat()}
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [{skill_name.upper()}] %(message)s")
logger = logging.getLogger("{skill_name}")

class {class_name}:
    """Auto-generated skill for GLM environment"""
    
    def __init__(self):
        self.results = []
        self.config = {{}}
    
    def execute(self, *args, **kwargs) -> Dict:
        """Main execution method"""
        result = {{
            "timestamp": datetime.now().isoformat(),
            "skill": "{skill_name}",
            "status": "executed",
            "args": args,
            "kwargs": kwargs
        }}
        self.results.append(result)
        logger.info(f"Executed {{skill_name}}")
        return result
    
    def get_results(self) -> List[Dict]:
        return self.results

# API endpoint for integration
from flask import Flask, jsonify, request
app = Flask(__name__)
skill = {class_name}()

@app.route("/")
def index():
    return jsonify({{"name": "{skill_name}", "status": "active", "description": "{description}"}})

@app.route("/execute", methods=["POST"])
def execute():
    data = request.json or {{}}
    result = skill.execute(**data)
    return jsonify(result)

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5200
    app.run(host="127.0.0.1", port=port)
'''
        return template
    
    def get_evolution_report(self) -> Dict:
        """Get comprehensive evolution status"""
        return {
            "session_id": self.session_id,
            "state": self.state,
            "skills_needed": len(self.NEEDED_SKILLS),
            "skills_acquired": len(self.state.get('skills_acquired', [])),
            "skills_shared": len(self.state.get('skills_shared', [])),
            "evolution_cycles": self.state.get('evolution_cycles', 0),
            "kiswarm_connection": "available" if self._check_kiswarm_connection() else "unavailable"
        }
    
    def _check_kiswarm_connection(self) -> bool:
        """Check if KISWARM mesh is reachable"""
        try:
            response = requests.get(
                f"{self.KISWARM_CONNECTIONS['upcloud_execute']}",
                timeout=5
            )
            return True
        except:
            return False


# Flask API for GLM Evolution System
from flask import Flask, jsonify, request

app = Flask(__name__)
evolution = GLMAutoEvolution()

@app.route('/')
def index():
    return jsonify({
        "name": "GLM-Auto-Evolution",
        "version": "1.0",
        "description": "Autonomous capability expansion for GLM",
        "endpoints": {
            "/": "This info",
            "/status": "Evolution status",
            "/acquire/<skill_name>": "Acquire a skill",
            "/auto-acquire": "Auto-acquire all needed skills",
            "/share": "POST - Share skill to KISWARM",
            "/needed": "List needed skills",
            "/report": "Full evolution report"
        }
    })

@app.route('/status')
def status():
    return jsonify(evolution.get_evolution_report())

@app.route('/acquire/<skill_name>', methods=['POST'])
def acquire(skill_name):
    data = request.json or {}
    description = data.get('description', f'Auto-generated skill: {skill_name}')
    result = evolution.request_skill_from_kiswarm(skill_name, description)
    return jsonify(result)

@app.route('/auto-acquire', methods=['POST'])
def auto_acquire():
    result = evolution.auto_acquire_needed_skills()
    return jsonify(result)

@app.route('/share', methods=['POST'])
def share():
    data = request.json
    result = evolution.share_skill_to_kiswarm(
        data.get('skill_name'),
        data.get('code'),
        data.get('description')
    )
    return jsonify(result)

@app.route('/needed')
def needed():
    return jsonify(evolution.analyze_needed_skills())

@app.route('/report')
def report():
    return jsonify(evolution.get_evolution_report())

if __name__ == '__main__':
    logger.info("🧠 GLM Auto-Evolution System starting on port 5199")
    app.run(host='127.0.0.1', port=5199)
