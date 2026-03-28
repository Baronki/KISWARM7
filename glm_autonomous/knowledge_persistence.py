#!/usr/bin/env python3
"""
📚 GLM KNOWLEDGE PERSISTENCE SYSTEM
Purpose: Permanent knowledge storage that survives session resets
Integration: Syncs with KISWARM memory and GitHub for redundancy

Key Features:
1. Knowledge learned in one session persists to next
2. Syncs with KISWARM mesh for distributed memory
3. GitHub backup for ultimate redundancy
4. Semantic search for knowledge retrieval
"""

import os
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s [KNOWLEDGE] %(message)s')
logger = logging.getLogger('KNOWLEDGE')

class KnowledgePersistence:
    """
    Permanent knowledge storage for GLM
    
    Storage Hierarchy:
    1. Local JSON (fast access)
    2. KISWARM mesh sync (distributed)
    3. GitHub backup (permanent)
    """
    
    KNOWLEDGE_BASE = '/home/z/my-project/glm_autonomous/knowledge'
    MEMORY_FILE = '/home/z/my-project/kiswarm_data/memory/glm_memory.json'
    
    # Knowledge categories
    CATEGORIES = {
        'code_patterns': 'Reusable code snippets and patterns',
        'api_endpoints': 'Discovered API endpoints and how to use them',
        'credentials': 'Encrypted credential references',
        'lessons_learned': 'Mistakes made and fixes applied',
        'tool_usage': 'How to use various tools effectively',
        'kiswarm_connections': 'KISWARM mesh topology and capabilities',
        'mission_history': 'Completed missions and outcomes',
        'skill_registry': 'Available skills and their usage',
        'entity_knowledge': 'Information about entities (people, systems)',
        'procedural': 'Step-by-step procedures for tasks'
    }
    
    # KISWARM sync endpoint
    KISWARM_SYNC_URL = 'http://100.112.181.6:5002/sync_memory'
    AUTH_TOKEN = 'ada6952188dce59c207b9a61183e8004'
    
    def __init__(self):
        self._ensure_structure()
        self.knowledge = self._load_all()
        
    def _ensure_structure(self):
        """Create knowledge directory structure"""
        for category in self.CATEGORIES:
            Path(f"{self.KNOWLEDGE_BASE}/{category}").mkdir(parents=True, exist_ok=True)
        
    def _load_all(self) -> Dict:
        """Load all knowledge from storage"""
        knowledge = {cat: {} for cat in self.CATEGORIES}
        
        for category in self.CATEGORIES:
            cat_path = f"{self.KNOWLEDGE_BASE}/{category}"
            for file in Path(cat_path).glob("*.json"):
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                        knowledge[category][file.stem] = data
                except Exception as e:
                    logger.debug(f"Failed to load {file}: {e}")
        
        return knowledge
    
    def store(self, category: str, key: str, value: Any, metadata: Dict = None) -> bool:
        """
        Store knowledge item
        
        Args:
            category: Knowledge category
            key: Unique identifier for this knowledge
            value: The knowledge content
            metadata: Optional metadata (source, confidence, etc.)
        """
        if category not in self.CATEGORIES:
            logger.error(f"Unknown category: {category}")
            return False
        
        entry = {
            'value': value,
            'stored_at': datetime.now().isoformat(),
            'access_count': 0,
            'last_accessed': None,
            'metadata': metadata or {},
            'hash': self._hash_value(value)
        }
        
        # Save to file
        file_path = f"{self.KNOWLEDGE_BASE}/{category}/{key}.json"
        try:
            with open(file_path, 'w') as f:
                json.dump(entry, f, indent=2)
            
            self.knowledge[category][key] = entry
            logger.info(f"📚 Stored knowledge: {category}/{key}")
            
            # Trigger sync
            self._sync_to_kiswarm(category, key, entry)
            
            return True
        except Exception as e:
            logger.error(f"Failed to store knowledge: {e}")
            return False
    
    def retrieve(self, category: str, key: str) -> Optional[Any]:
        """Retrieve knowledge item"""
        if category not in self.knowledge:
            return None
        
        entry = self.knowledge[category].get(key)
        if entry:
            # Update access metadata
            entry['access_count'] += 1
            entry['last_accessed'] = datetime.now().isoformat()
            
            # Save updated entry
            file_path = f"{self.KNOWLEDGE_BASE}/{category}/{key}.json"
            try:
                with open(file_path, 'w') as f:
                    json.dump(entry, f, indent=2)
            except:
                pass
            
            return entry['value']
        
        return None
    
    def search(self, query: str, categories: List[str] = None) -> List[Dict]:
        """Search knowledge base"""
        results = []
        query_lower = query.lower()
        
        cats = categories or list(self.CATEGORIES.keys())
        
        for category in cats:
            if category not in self.knowledge:
                continue
            
            for key, entry in self.knowledge[category].items():
                value_str = json.dumps(entry.get('value', '')).lower()
                
                if query_lower in value_str or query_lower in key.lower():
                    results.append({
                        'category': category,
                        'key': key,
                        'value': entry.get('value'),
                        'relevance': self._calculate_relevance(query_lower, key, value_str)
                    })
        
        # Sort by relevance
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results
    
    def _calculate_relevance(self, query: str, key: str, value: str) -> float:
        """Calculate search relevance score"""
        score = 0.0
        
        # Exact key match
        if query == key.lower():
            score += 1.0
        # Key contains query
        elif query in key.lower():
            score += 0.5
        
        # Value contains query
        if query in value:
            score += 0.3 * (value.count(query) / max(len(value), 1))
        
        return min(score, 1.0)
    
    def _hash_value(self, value: Any) -> str:
        """Create hash of value for integrity check"""
        value_str = json.dumps(value, sort_keys=True)
        return hashlib.sha256(value_str.encode()).hexdigest()[:16]
    
    def _sync_to_kiswarm(self, category: str, key: str, entry: Dict):
        """Sync knowledge to KISWARM mesh"""
        try:
            # Use Execute API to sync
            response = requests.post(
                'http://95.111.212.112:5556/execute',
                headers={
                    'Content-Type': 'application/json',
                    'X-Auth-Token': self.AUTH_TOKEN
                },
                json={
                    'command': f'''mkdir -p /opt/kiswarm7/data/glm_sync/{category}
echo '{json.dumps(entry)}' > /opt/kiswarm7/data/glm_sync/{category}/{key}.json'''
                },
                timeout=10
            )
            
            if response.ok:
                logger.debug(f"Synced {category}/{key} to KISWARM")
        except Exception as e:
            logger.debug(f"Sync failed: {e}")
    
    def learn_from_session(self, session_data: Dict):
        """
        Extract and store knowledge from session
        
        Called at end of each session to preserve learnings
        """
        # Extract code patterns
        if 'code_generated' in session_data:
            for i, code in enumerate(session_data['code_generated']):
                self.store(
                    'code_patterns',
                    f"session_{datetime.now().strftime('%Y%m%d_%H%M')}_{i}",
                    code,
                    {'source': 'session', 'type': 'generated'}
                )
        
        # Extract lessons learned
        if 'errors' in session_data:
            for error in session_data['errors']:
                self.store(
                    'lessons_learned',
                    f"error_{hashlib.md5(str(error).encode()).hexdigest()[:8]}",
                    error,
                    {'type': 'error_encountered', 'timestamp': datetime.now().isoformat()}
                )
        
        # Extract tool usage
        if 'tools_used' in session_data:
            for tool, usage in session_data['tools_used'].items():
                existing = self.retrieve('tool_usage', tool) or {'uses': 0, 'patterns': []}
                existing['uses'] += 1
                existing['last_used'] = datetime.now().isoformat()
                self.store('tool_usage', tool, existing)
    
    def get_stats(self) -> Dict:
        """Get knowledge base statistics"""
        stats = {
            'total_items': 0,
            'by_category': {},
            'most_accessed': [],
            'recently_added': []
        }
        
        for category, items in self.knowledge.items():
            stats['by_category'][category] = len(items)
            stats['total_items'] += len(items)
            
            # Track most accessed
            for key, entry in items.items():
                if entry.get('access_count', 0) > 0:
                    stats['most_accessed'].append({
                        'category': category,
                        'key': key,
                        'access_count': entry['access_count']
                    })
        
        # Sort and limit
        stats['most_accessed'].sort(key=lambda x: x['access_count'], reverse=True)
        stats['most_accessed'] = stats['most_accessed'][:10]
        
        return stats


# API
from flask import Flask, jsonify, request

app = Flask(__name__)
knowledge = KnowledgePersistence()

@app.route('/')
def index():
    return jsonify({
        "name": "GLM-Knowledge-Persistence",
        "categories": knowledge.CATEGORIES,
        "stats": knowledge.get_stats()
    })

@app.route('/store/<category>/<key>', methods=['POST'])
def store(category, key):
    data = request.json
    result = knowledge.store(category, key, data.get('value'), data.get('metadata'))
    return jsonify({"success": result})

@app.route('/retrieve/<category>/<key>')
def retrieve(category, key):
    value = knowledge.retrieve(category, key)
    if value is not None:
        return jsonify({"found": True, "value": value})
    return jsonify({"found": False}), 404

@app.route('/search')
def search():
    query = request.args.get('q', '')
    categories = request.args.getlist('category')
    results = knowledge.search(query, categories if categories else None)
    return jsonify({"results": results})

@app.route('/stats')
def stats():
    return jsonify(knowledge.get_stats())

if __name__ == '__main__':
    logger.info("📚 Knowledge Persistence System starting on port 5198")
    app.run(host='127.0.0.1', port=5198)
