#!/usr/bin/env python3
"""
🌀 HERMES EDGE NODE - GLM Environment
=====================================
Lightweight Hermes for edge processing

Role: EDGE
Master: 100.112.181.6 (UpCloud)
Local: 100.125.201.100 (GLM)

Features:
- Local skill execution
- Memory sync with master
- Low-latency operations
- Failover support
"""

import os
import sys
import json
import time
import logging
import threading
import requests
import hashlib
from datetime import datetime
from collections import deque
from typing import Dict, List, Any, Optional

try:
    import ollama
    OLLAMA_AVAILABLE = True
except:
    OLLAMA_AVAILABLE = False

# ============================================================
# EDGE CONFIGURATION
# ============================================================

HERMES_DIR = "/opt/hermes_edge"
MEMORY_DIR = os.path.join(HERMES_DIR, "memory")
SKILLS_DIR = os.path.join(HERMES_DIR, "skills")
LOGS_DIR = os.path.join(HERMES_DIR, "logs")
STATE_DIR = os.path.join(HERMES_DIR, "state")

# Master connection
MASTER_IP = "100.112.181.6"
MASTER_PORT = 5000
MASTER_API = f"http://{MASTER_IP}:{MASTER_PORT}"

# Local config
LOCAL_IP = "100.125.201.100"
OLLAMA_PORT = 11434

# Telegram (from master)
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
ADMIN_CHAT = "YOUR_ADMIN_CHAT_ID_HERE"

# Create directories
for d in [HERMES_DIR, MEMORY_DIR, SKILLS_DIR, LOGS_DIR, STATE_DIR]:
    os.makedirs(d, exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [EDGE] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, "hermes_edge.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("HERMES-EDGE")


# ============================================================
# EDGE MEMORY SYSTEM
# ============================================================

class EdgeMemory:
    """Memory system with master sync capability"""
    
    def __init__(self):
        self.layer_1 = deque(maxlen=100)  # Local short-term
        self.layer_2_dir = os.path.join(MEMORY_DIR, "important")
        os.makedirs(self.layer_2_dir, exist_ok=True)
        
        self.sync_interval = 300  # 5 minutes
        self.last_sync = None
        self.master_connected = False
        
        self._load_local()
        logger.info("Edge Memory initialized")
    
    def _load_local(self):
        """Load local memories"""
        try:
            with open(os.path.join(MEMORY_DIR, "local.json"), 'r') as f:
                data = json.load(f)
                for m in data.get('layer1', []):
                    self.layer_1.append(m)
        except:
            pass
    
    def _save_local(self):
        """Save local memories"""
        with open(os.path.join(MEMORY_DIR, "local.json"), 'w') as f:
            json.dump({'layer1': list(self.layer_1)}, f)
    
    def store(self, content: str, importance: float = 0.5, tags: List[str] = None):
        """Store memory locally"""
        memory = {
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'importance': importance,
            'tags': tags or [],
            'source': 'edge'
        }
        
        self.layer_1.append(memory)
        self._save_local()
        
        # Sync to master if important
        if importance > 0.7 and self.master_connected:
            self._push_to_master(memory)
    
    def _push_to_master(self, memory: Dict):
        """Push important memory to master"""
        try:
            requests.post(
                f"{MASTER_API}/api/memory/sync",
                json={'memory': memory, 'source': 'edge'},
                timeout=10
            )
        except Exception as e:
            logger.error(f"Failed to push to master: {e}")
    
    def sync_from_master(self) -> Dict:
        """Pull memories from master"""
        if not self.check_master():
            return {'synced': False, 'reason': 'master_offline'}
        
        try:
            r = requests.get(f"{MASTER_API}/api/memory/export", timeout=30)
            if r.status_code == 200:
                data = r.json()
                # Merge with local memories
                for m in data.get('memories', []):
                    if m not in list(self.layer_1):
                        self.layer_1.append(m)
                self._save_local()
                self.last_sync = datetime.now().isoformat()
                return {'synced': True, 'count': len(data.get('memories', []))}
        except Exception as e:
            logger.error(f"Sync from master failed: {e}")
        
        return {'synced': False}
    
    def check_master(self) -> bool:
        """Check if master is reachable"""
        try:
            r = requests.get(f"{MASTER_API}/health", timeout=5)
            self.master_connected = r.status_code == 200
        except:
            self.master_connected = False
        return self.master_connected
    
    def get_status(self) -> Dict:
        """Get memory status"""
        return {
            'local_memories': len(self.layer_1),
            'master_connected': self.master_connected,
            'last_sync': self.last_sync
        }


# ============================================================
# EDGE OLLAMA ENGINE
# ============================================================

class EdgeOllama:
    """Local Ollama with master fallback"""
    
    def __init__(self):
        self.local_url = f"http://localhost:{OLLAMA_PORT}"
        self.model = "qwen2.5:14b"  # Default model
        self.available = self._check_local()
        logger.info(f"Ollama: {'available' if self.available else 'unavailable'}")
    
    def _check_local(self) -> bool:
        """Check if local Ollama is available"""
        try:
            r = requests.get(f"{self.local_url}/api/tags", timeout=5)
            return r.status_code == 200
        except:
            return False
    
    def chat(self, messages: List[Dict], **kwargs) -> str:
        """Chat via local Ollama"""
        if not self.available:
            return "Ollama not available locally. Please start Ollama service."
        
        try:
            if OLLAMA_AVAILABLE:
                r = ollama.chat(model=self.model, messages=messages, **kwargs)
                return r.get('message', {}).get('content', '')
            else:
                r = requests.post(
                    f"{self.local_url}/api/chat",
                    json={'model': self.model, 'messages': messages, 'stream': False},
                    timeout=120
                )
                if r.status_code == 200:
                    return r.json().get('message', {}).get('content', '')
        except Exception as e:
            logger.error(f"Ollama error: {e}")
        
        return None
    
    def generate(self, prompt: str) -> str:
        """Simple generation"""
        return self.chat([{'role': 'user', 'content': prompt}])


# ============================================================
# EDGE SKILL SYSTEM
# ============================================================

class EdgeSkills:
    """Local skill execution with master sync"""
    
    def __init__(self, memory: EdgeMemory, ollama: EdgeOllama):
        self.skills_dir = SKILLS_DIR
        self.skills = {}
        self.memory = memory
        self.ollama = ollama
        self._load_skills()
        self._init_edge_skills()
        logger.info(f"Skills: {len(self.skills)} loaded")
    
    def _load_skills(self):
        """Load skills from disk"""
        for f in os.listdir(self.skills_dir):
            if f.endswith('.json'):
                try:
                    with open(os.path.join(self.skills_dir, f), 'r') as fp:
                        skill = json.load(fp)
                        self.skills[skill['name']] = skill
                except:
                    pass
    
    def _init_edge_skills(self):
        """Initialize edge-specific skills"""
        
        edge_skills = [
            {
                "name": "local_health_check",
                "description": "Check local system health",
                "code": '''
import os
import subprocess

result = {"healthy": True, "checks": {}}

# Check disk
df = subprocess.run("df -h / | tail -1", shell=True, capture_output=True, text=True)
result["checks"]["disk"] = df.stdout.strip()

# Check memory
mem = subprocess.run("free -h | grep Mem", shell=True, capture_output=True, text=True)
result["checks"]["memory"] = mem.stdout.strip()

# Check Ollama
try:
    import requests
    r = requests.get("http://localhost:11434/api/tags", timeout=5)
    result["checks"]["ollama"] = "OK" if r.status_code == 200 else "ERROR"
except:
    result["checks"]["ollama"] = "OFFLINE"
    result["healthy"] = False

return result
''',
                "category": "monitoring"
            },
            {
                "name": "sync_to_master",
                "description": "Force sync with master node",
                "code": '''
result = {"synced": False}

if memory.master_connected:
    sync_result = memory.sync_from_master()
    result = sync_result
else:
    result["error"] = "Master not connected"

return result
''',
                "category": "sync"
            },
            {
                "name": "edge_think",
                "description": "Local thinking with memory",
                "code": '''
topic = kwargs.get('topic', 'What should I focus on?')

# Get relevant memories
memories = memory.layer_1

# Build context
context = f"Topic: {topic}\\nRecent memories: {len(memories)}"

# Generate thought
thought = ollama.generate(f"Think briefly about: {topic}. Be concise.")
result = {"thought": thought, "memories_used": len(memories)}

# Store this thinking
memory.store(f"Thought about: {topic}", 0.6, ['thinking'])

return result
''',
                "category": "thinking"
            }
        ]
        
        for skill in edge_skills:
            if skill['name'] not in self.skills:
                self.learn(skill['name'], skill['description'], skill['code'], skill.get('category', 'general'))
    
    def learn(self, name: str, description: str, code: str, category: str = "general"):
        """Learn a new skill"""
        skill = {
            'name': name,
            'description': description,
            'code': code,
            'category': category,
            'created': datetime.now().isoformat(),
            'usage_count': 0,
            'source': 'edge'
        }
        
        self.skills[name] = skill
        with open(os.path.join(self.skills_dir, f"{name}.json"), 'w') as f:
            json.dump(skill, f, indent=2)
        
        logger.info(f"Skill learned: {name}")
    
    def execute(self, name: str, **kwargs) -> Any:
        """Execute a skill"""
        if name not in self.skills:
            return {"error": f"Skill not found: {name}"}
        
        skill = self.skills[name]
        
        exec_globals = {
            'kwargs': kwargs,
            'result': None,
            'memory': self.memory,
            'ollama': self.ollama,
            'MASTER_IP': MASTER_IP,
            'LOCAL_IP': LOCAL_IP
        }
        
        try:
            exec(skill['code'], exec_globals)
            result = exec_globals.get('result')
            
            skill['usage_count'] = skill.get('usage_count', 0) + 1
            with open(os.path.join(self.skills_dir, f"{name}.json"), 'w') as f:
                json.dump(skill, f, indent=2)
            
            return result
        except Exception as e:
            logger.error(f"Skill execution error ({name}): {e}")
            return {"error": str(e)}


# ============================================================
# EDGE TELEGRAM (Minimal)
# ============================================================

class EdgeTelegram:
    """Minimal Telegram interface for edge"""
    
    def __init__(self, edge):
        self.edge = edge
        self.last_update_id = 0
        self.running = False
    
    def send(self, text: str, chat_id: int = None) -> bool:
        """Send message to Telegram"""
        try:
            requests.post(
                f"{TELEGRAM_API}/sendMessage",
                json={'chat_id': chat_id or ADMIN_CHAT, 'text': text[:4096]},
                timeout=30
            )
            return True
        except:
            return False
    
    def report_status(self):
        """Report edge status to admin"""
        status = self.edge.get_status()
        msg = f"""🌀 EDGE HERMES STATUS
==================
IP: {LOCAL_IP}
Master: {'🟢' if status['master_connected'] else '🔴'} {MASTER_IP}
Memories: {status['memory']['local_memories']}
Skills: {status['skills']}
Last Sync: {status['memory'].get('last_sync', 'Never')}

Edge Node Active - GLM Environment"""
        self.send(msg)
    
    def run(self):
        """Run Telegram listener"""
        self.running = True
        logger.info("Telegram listener started")
        
        while self.running:
            try:
                r = requests.get(
                    f"{TELEGRAM_API}/getUpdates",
                    params={'offset': self.last_update_id + 1, 'timeout': 30},
                    timeout=60
                )
                
                if r.status_code == 200:
                    for update in r.json().get('result', []):
                        self.last_update_id = update.get('update_id', 0)
                        msg = update.get('message', {})
                        text = msg.get('text', '')
                        
                        if text == '/edge_status':
                            self.report_status()
                        elif text == '/edge_sync':
                            result = self.edge.skills.execute('sync_to_master')
                            self.send(f"Sync result: {result}")
                
                time.sleep(1)
            except Exception as e:
                logger.error(f"Telegram error: {e}")
                time.sleep(5)
    
    def stop(self):
        self.running = False


# ============================================================
# HERMES EDGE AGENT
# ============================================================

class HermesEdge:
    """Main Edge Hermes Agent"""
    
    def __init__(self):
        self.identity = {
            'name': 'Hermes-Edge-GLM',
            'uuid': 'glm-edge-100-125-201-100',
            'version': '1.0.0',
            'role': 'EDGE',
            'master': MASTER_IP
        }
        
        self.memory = EdgeMemory()
        self.ollama = EdgeOllama()
        self.skills = EdgeSkills(self.memory, self.ollama)
        self.telegram = None
        
        self.running = False
        self.iteration = 0
        
        logger.info(f"🌀 Hermes Edge: {self.identity['uuid']}")
    
    def get_status(self) -> Dict:
        """Get full status"""
        return {
            'running': self.running,
            'identity': self.identity,
            'memory': self.memory.get_status(),
            'skills': len(self.skills.skills),
            'master_connected': self.memory.check_master(),
            'ollama_available': self.ollama.available,
            'iterations': self.iteration
        }
    
    def register_with_master(self) -> bool:
        """Register this edge node with master"""
        if not self.memory.check_master():
            return False
        
        try:
            r = requests.post(
                f"{MASTER_API}/api/edge/register",
                json={
                    'identity': self.identity,
                    'status': self.get_status()
                },
                timeout=10
            )
            return r.status_code == 200
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return False
    
    def run(self):
        """Main edge loop"""
        logger.info("🌀 Hermes Edge starting...")
        self.running = True
        
        # Start Telegram
        self.telegram = EdgeTelegram(self)
        threading.Thread(target=self.telegram.run, daemon=True).start()
        
        # Store startup
        self.memory.store("Hermes Edge started", 0.8, ['startup'])
        
        # Initial master check
        master_ok = self.memory.check_master()
        logger.info(f"Master: {'ONLINE' if master_ok else 'OFFLINE'}")
        
        if master_ok:
            self.register_with_master()
            self.memory.sync_from_master()
        
        # Notify admin
        self.telegram.report_status()
        
        # Main loop
        while self.running:
            try:
                self.iteration += 1
                
                # Check master periodically
                if self.iteration % 10 == 0:
                    master_ok = self.memory.check_master()
                    if master_ok:
                        self.register_with_master()
                    
                    # Sync memories
                    if self.iteration % 30 == 0 and master_ok:
                        self.memory.sync_from_master()
                
                # Health check
                if self.iteration % 60 == 0:
                    health = self.skills.execute('local_health_check')
                    if not health.get('healthy'):
                        logger.warning(f"Health check failed: {health}")
                
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Loop error: {e}")
                time.sleep(30)
    
    def stop(self):
        """Stop edge agent"""
        self.running = False
        if self.telegram:
            self.telegram.stop()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    logger.info("🌀 HERMES EDGE NODE v1.0")
    logger.info(f"🌀 Master: {MASTER_IP}")
    logger.info(f"🌀 Local: {LOCAL_IP}")
    
    edge = HermesEdge()
    
    try:
        edge.run()
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
        edge.stop()
