# GLM EDGE NODE RECONNECTION GUIDE

## Current Status (2026-03-29)

| Node | IP | Status | Last Seen |
|------|-----|--------|-----------|
| UpCloud (Master) | 100.112.181.6 | 🟢 ONLINE | Active |
| GLM (Edge) | 100.125.201.100 | 🔴 OFFLINE | 21h ago |
| OpenClaw (Backup) | 100.113.1.85 | 🔴 OFFLINE | 21h ago |
| sah6 | 100.92.174.24 | 🟢 ONLINE | Active |

## GLM Reconnection Steps

When GLM comes back online, perform these steps:

### Step 1: Reconnect Tailscale
```bash
# On GLM environment (100.125.201.100)
sudo tailscale up --auth-key=tskey-auth-kYzoboKgtK11CNTRL-cAh5zWNeygaKa2LEtAg8haF773px2SjY

# Or if Tailscale is not installed:
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --auth-key=tskey-auth-kYzoboKgtK11CNTRL-cAh5zWNeygaKa2LEtAg8haF773px2SjY
```

### Step 2: Verify Connection
```bash
# Check Tailscale status
tailscale status

# Should show:
# 100.112.181.6  ubuntu-8cpu-16gb-us-sjo1  linux  -
# 100.125.201.100  glm-autonomous            linux  -  (this machine)
```

### Step 3: Deploy Edge Hermes
```bash
# Clone from GitHub or copy from master
mkdir -p /opt/hermes_edge
cd /opt/hermes_edge

# Download from GitHub
curl -sL https://raw.githubusercontent.com/Baronki/KISWARM7/main/hermes/hermes_edge.py -o hermes_edge.py

# Or copy from master via Tailscale
scp root@100.112.181.6:/opt/hermes_edge_deployment/hermes_edge.py .

# Start Edge Hermes
python3 hermes_edge.py
```

### Step 4: Verify Edge Node
```bash
# Check memory sync with master
curl http://100.112.181.6:6000/health

# Check local health
curl http://localhost:5000/health
```

## Pre-Deployed Files on Master (UpCloud)

All files are ready on UpCloud in `/opt/hermes_edge_deployment/`:

- `hermes_edge.py` - Edge Hermes agent
- Automatic deployment will trigger when GLM comes online

## Memory Sync API

The memory sync API is running on Master at port 6000:

```bash
# Health check
curl http://100.112.181.6:6000/health

# Expected response:
# {"port":5002,"service":"memory_sync","status":"healthy"}
```

## Watch Script

The GLM watch script is running on UpCloud:

```bash
# Check watch script log
tail -f /opt/hermes/logs/glm_watch.log

# When GLM comes online, it will:
# 1. Send Telegram notification
# 2. Initiate Edge Hermes deployment
```

## Failover Protocol

```
┌─────────────────────────────────────────────────────┐
│                 FAILOVER FLOW                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│  1. Master (UpCloud) goes offline                   │
│          ↓                                           │
│  2. Edge detects master unreachable                 │
│          ↓                                           │
│  3. Edge sends Telegram alert                       │
│          ↓                                           │
│  4. Edge continues local operations                 │
│          ↓                                           │
│  5. Master returns, sync resumes                    │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## Telegram Commands

When GLM Edge is online:

- `/edge_status` - Get edge node status
- `/edge_sync` - Force sync with master
- `/mesh` - Full mesh status

## Expected Timeline

1. **GLM reconnects to Tailscale** → Instant
2. **Watch script detects** → Within 60 seconds
3. **Edge Hermes deploys** → 1-2 minutes
4. **Memory sync completes** → 1 minute

## Troubleshooting

### Tailscale not connecting?
```bash
# Restart Tailscale
sudo systemctl restart tailscaled

# Check logs
sudo journalctl -u tailscaled -f
```

### Edge Hermes not starting?
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Install Ollama if needed
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
```

### Memory sync failing?
```bash
# Check master connectivity
ping 100.112.181.6

# Check memory sync API
curl http://100.112.181.6:6000/health
```

---

*Created: 2026-03-29*
*Last Updated: 2026-03-29*
