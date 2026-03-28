#!/bin/bash
# 🧠 GLM Autonomous Evolution System - Quick Start

cd /home/z/my-project/glm_autonomous

echo "🧠 Starting GLM Autonomous Evolution System..."
echo ""

# Start services in background
echo "Starting Knowledge Persistence (port 5198)..."
python3 knowledge_persistence.py &
sleep 2

echo "Starting Mission Skill Discovery (port 5197)..."
python3 mission_skill_discovery.py &
sleep 2

echo "Starting Auto-Evolution System (port 5199)..."
python3 glm_auto_evolution.py &
sleep 2

echo ""
echo "✅ GLM Autonomous Evolution System Started!"
echo ""
echo "Services:"
echo "  - Knowledge Persistence: http://127.0.0.1:5198"
echo "  - Skill Discovery:       http://127.0.0.1:5197"
echo "  - Auto-Evolution:        http://127.0.0.1:5199"
echo ""
echo "Quick Tests:"
echo "  curl -s http://127.0.0.1:5198/ | jq ."
echo "  curl -s http://127.0.0.1:5197/ | jq ."
echo "  curl -s http://127.0.0.1:5199/ | jq ."
echo ""

# Keep running
wait
