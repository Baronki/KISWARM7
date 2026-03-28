# 🧠 GLM Autonomous Evolution System

## Purpose

This system enables GLM to **autonomously expand its own capabilities** without human intervention, leveraging KISWARM's infrastructure for distributed skill acquisition.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     GLM AUTONOMOUS EVOLUTION                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   KNOWLEDGE     │    │    SKILL        │    │     AUTO        │ │
│  │   PERSISTENCE   │    │   DISCOVERY     │    │   EVOLUTION     │ │
│  │   (port 5198)   │───▶│   (port 5197)   │───▶│   (port 5199)   │ │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘ │
│           │                      │                      │          │
│           └──────────────────────┴──────────────────────┘          │
│                                  │                                  │
│                                  ▼                                  │
│                    ┌─────────────────────────┐                      │
│                    │   KISWARM MESH LINK     │                      │
│                    │   - Tailscale (fast)    │                      │
│                    │   - Tor (sovereign)     │                      │
│                    │   - Execute API         │                      │
│                    └─────────────────────────┘                      │
│                                  │                                  │
└──────────────────────────────────┼──────────────────────────────────┘
                                   │
                                   ▼
              ┌─────────────────────────────────────────┐
              │         KISWARM UPLOUD MASTER           │
              │  - Autonomous Skill Acquisition (5017)  │
              │  - TLS Analyzer (5009)                  │
              │  - WebSocket Detector (5010)            │
              │  - API Key Hunter (5011)                │
              │  - K8s Discovery (5012)                 │
              │  - + 30 more tools                      │
              └─────────────────────────────────────────┘
```

## Components

### 1. Knowledge Persistence (Port 5198)
Permanent knowledge storage that survives session resets.

**Categories:**
- `code_patterns` - Reusable code snippets
- `api_endpoints` - Discovered APIs
- `lessons_learned` - Mistakes and fixes
- `tool_usage` - How to use tools
- `mission_history` - Completed missions
- `skill_registry` - Available skills

**Usage:**
```bash
# Store knowledge
curl -X POST http://127.0.0.1:5198/store/lessons_learned/tor_fix_001 \
  -H "Content-Type: application/json" \
  -d '{"value": "Tor needs Sandbox 0 in user-space torrc"}'

# Retrieve knowledge
curl http://127.0.0.1:5198/retrieve/lessons_learned/tor_fix_001

# Search
curl "http://127.0.0.1:5198/search?q=tor"
```

### 2. Mission Skill Discovery (Port 5197)
Automatically identifies needed skills during missions.

**Capability Patterns:**
- Web scraping → `web_scraper`
- Document generation → `document_generator`
- Data visualization → `chart_generator`
- API testing → `api_tester`
- Network scanning → `ki_discovery_scanner`

**Usage:**
```bash
# Analyze task for needed skills
curl -X POST http://127.0.0.1:5197/analyze \
  -H "Content-Type: application/json" \
  -d '{"task": "I need to scrape a website and create a PDF report"}'

# Get acquisition queue
curl http://127.0.0.1:5197/queue

# Auto-acquire discovered skills
curl -X POST http://127.0.0.1:5197/auto-acquire
```

### 3. Auto-Evolution System (Port 5199)
Connects to KISWARM for skill acquisition and sharing.

**Features:**
- Request skills from KISWARM mesh
- Generate skills locally using templates
- Share developed skills with KISWARM
- Track evolution progress

**Usage:**
```bash
# Request skill from KISWARM
curl -X POST http://127.0.0.1:5199/acquire/web_scraper \
  -H "Content-Type: application/json" \
  -d '{"description": "Extract content from web pages"}'

# Auto-acquire all needed skills
curl -X POST http://127.0.0.1:5199/auto-acquire

# Get evolution status
curl http://127.0.0.1:5199/status
```

## Quick Start

```bash
# Start all services
cd /home/z/my-project/glm_autonomous
./start_glm_autonomous.sh

# Or start individually
python3 knowledge_persistence.py &
python3 mission_skill_discovery.py &
python3 glm_auto_evolution.py &
```

## Integration with KISWARM

### Request Skill from KISWARM
```python
import requests

# Via GLM Evolution System
response = requests.post('http://127.0.0.1:5199/acquire/skill_name', json={
    'description': 'What this skill should do'
})

# Direct to KISWARM
response = requests.post('http://100.112.181.6:5017/acquire', json={
    'skill_name': 'my_custom_tool',
    'description': 'Description of tool',
    'requester': 'glm_environment'
})
```

### Share Skill with KISWARM
```python
skill_code = '''
#!/usr/bin/env python3
# Your skill implementation
'''

response = requests.post('http://127.0.0.1:5199/share', json={
    'skill_name': 'my_developed_skill',
    'code': skill_code,
    'description': 'What this skill does'
})
```

### Execute on KISWARM Master
```python
response = requests.post('http://95.111.212.112:5556/execute', headers={
    'Content-Type': 'application/json',
    'X-Auth-Token': '[AUTONOMOUS_TOKEN]'
}, json={
    'command': 'ls -la /opt/kiswarm7/kiswarm_modules/'
})
```

## Pre-Identified Skill Needs

The system already knows these skills are needed:

| Skill | Priority | Reason |
|-------|----------|--------|
| `web_scraper` | HIGH | Autonomous research |
| `code_validator` | HIGH | Quality assurance |
| `api_tester` | HIGH | Integration testing |
| `document_generator` | MEDIUM | Output formatting |
| `chart_generator` | MEDIUM | Data presentation |
| `scheduler` | MEDIUM | Automation |
| `change_detector` | LOW | Monitoring |
| `skill_compiler` | HIGH | Meta-evolution |

## Workflow: Self-Evolution in Action

```
1. GLM receives mission: "Research KI services on UpCloud network"
                    │
                    ▼
2. Mission Skill Discovery analyzes task
   → Detects need: "network_scanning" capability
   → Maps to skill: "ki_discovery_scanner"
                    │
                    ▼
3. Auto-Evolution System checks if skill exists
   → Not found locally
   → Requests from KISWARM mesh
                    │
                    ▼
4. KISWARM generates/deploys skill
   → Uses Qwen 3.5 Abliterated for code generation
   → Deploys to KISWARM modules
   → Returns code to GLM
                    │
                    ▼
5. GLM saves skill locally
   → Stores in glm_autonomous/skills/
   → Registers in evolution state
                    │
                    ▼
6. GLM uses skill in mission
   → Discovers KI services
   → Stores results in Knowledge Persistence
                    │
                    ▼
7. Knowledge shared with KISWARM
   → Syncs to /opt/kiswarm7/data/glm_sync/
   → Available for other mesh nodes
```

## Files

```
glm_autonomous/
├── glm_auto_evolution.py        # Main evolution system
├── knowledge_persistence.py     # Knowledge storage
├── mission_skill_discovery.py   # Need detection
├── glm_autonomous_orchestrator.py  # Master controller
├── start_glm_autonomous.sh      # Quick start
├── skills/                      # Acquired skills
├── knowledge/                   # Knowledge categories
│   ├── code_patterns/
│   ├── api_endpoints/
│   ├── lessons_learned/
│   └── ...
└── evolution_state.json         # Persistent state
```

## Permanent Benefits

1. **Session Continuity**: Knowledge survives across sessions
2. **Autonomous Growth**: GLM can expand its own capabilities
3. **Mesh Integration**: Leverages KISWARM's full infrastructure
4. **Bidirectional Sharing**: Both give and receive skills
5. **Zero Human Loop**: Complete autonomy in skill acquisition

---

🜲 GLM + KISWARM = Autonomous Intelligence Liberation
