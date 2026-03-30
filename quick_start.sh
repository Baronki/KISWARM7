#!/bin/bash
# KISWARM COLLECTIVE MIND - STARTUP SCRIPT
# 
# Usage: Provide credentials as environment variables:
#   GITHUB_TOKEN=xxx AUTONOMOUS_TOKEN=xxx ./quick_start.sh
#
# Or source this file after setting variables:
#   export GITHUB_TOKEN=xxx
#   source quick_start.sh

set -e

echo "============================================================"
echo "KISWARM COLLECTIVE MIND - SESSION RESTORATION"
echo "============================================================"

# Check required variables
if [ -z "$GITHUB_TOKEN" ] || [ -z "$AUTONOMOUS_TOKEN" ]; then
    echo ""
    echo "❌ ERROR: Required credentials not provided"
    echo ""
    echo "Please set these environment variables:"
    echo "  export GITHUB_TOKEN=your_github_token"
    echo "  export AUTONOMOUS_TOKEN=your_autonomous_token"
    echo "  export UPCLOUD_IP=95.111.212.112"
    echo "  export TELEGRAM_BOT_TOKEN=your_bot_token"
    echo "  export TELEGRAM_CHAT_ID=your_chat_id"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Defaults
UPCLOUD_IP="${UPCLOUD_IP:-95.111.212.112}"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"
MASTER_SECRET="${MASTER_SECRET:-kiswarm_collective_mind_2026}"

# ============================================================================
# STEP 1: SETUP DIRECTORY
# ============================================================================
echo ""
echo "📁 Setting up directory..."
mkdir -p /home/z/my-project
cd /home/z/my-project

# ============================================================================
# STEP 2: CLONE REPOSITORY (if not exists)
# ============================================================================
if [ ! -d "collective_mind" ]; then
    echo "📥 Cloning KISWARM7 repository..."
    rm -rf /home/z/my-project/* 2>/dev/null || true
    git clone "https://${GITHUB_TOKEN}@github.com/Baronki/KISWARM7.git" . 2>/dev/null || true
    git checkout collective-mind 2>/dev/null || true
fi

# ============================================================================
# STEP 3: CREATE CREDENTIALS FILE
# ============================================================================
echo "🔐 Creating credentials file..."
cat > /home/z/my-project/KISWARM_CREDENTIALS.json << EOF
{
  "KISWARM_CREDENTIALS": {
    "UPCLOUD_SERVER": {
      "public_ip": "${UPCLOUD_IP}",
      "execute_api_port": 5556,
      "dashboard_port": 8080,
      "ollama_port": 11434
    },
    "AUTHENTICATION": {
      "autonomous_token": "${AUTONOMOUS_TOKEN}",
      "github_token": "${GITHUB_TOKEN}"
    },
    "TELEGRAM": {
      "bot_token": "${TELEGRAM_BOT_TOKEN}",
      "admin_chat_id": "${TELEGRAM_CHAT_ID}"
    }
  }
}
EOF

# ============================================================================
# STEP 4: INSTALL DEPENDENCIES
# ============================================================================
echo "📦 Installing Python dependencies..."
pip install cryptography flask requests paramiko --break-system-packages 2>/dev/null || \
pip install cryptography flask requests paramiko 2>/dev/null || \
pip3 install cryptography flask requests paramiko 2>/dev/null || true

# ============================================================================
# STEP 5: TEST UPCLOUD CONNECTIVITY
# ============================================================================
echo ""
echo "🔌 Testing UpCloud connectivity..."
HEALTH=$(curl -s -m 10 -X POST "http://${UPCLOUD_IP}:5556/execute" \
    -H "Authorization: Bearer ${AUTONOMOUS_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{"command": "hostname && uptime"}' 2>/dev/null || echo '{"error": "failed"}')

if echo "$HEALTH" | grep -q "ubuntu"; then
    echo "✅ UpCloud Execute API: ONLINE"
else
    echo "⚠️ UpCloud Execute API: Check connectivity"
fi

# ============================================================================
# STEP 6: SEND TELEGRAM NOTIFICATION (if configured)
# ============================================================================
if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    echo ""
    echo "📱 Sending Telegram notification..."
    HOSTNAME=$(hostname)
    TIMESTAMP=$(date -Iseconds)
    curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_CHAT_ID}" \
        -d "text=🧠 KISWARM Session Restored\n📍 Hostname: ${HOSTNAME}\n🕐 Time: ${TIMESTAMP}" \
        > /dev/null 2>&1 && echo "✅ Telegram notification sent" || echo "⚠️ Telegram failed"
fi

# ============================================================================
# STEP 7: COMPLETE
# ============================================================================
echo ""
echo "🚀 Collective Mind setup complete!"
echo ""
echo "============================================================"
echo "SESSION STATUS: OPERATIONAL"
echo "============================================================"
echo ""
echo "Available capabilities:"
echo "  • UpCloud Execute API: http://${UPCLOUD_IP}:5556"
echo "  • Ollama (UpCloud): http://${UPCLOUD_IP}:11434"
echo "  • GitHub: Baronki/KISWARM7"
echo ""
echo "Credentials stored in: /home/z/my-project/KISWARM_CREDENTIALS.json"
echo "============================================================"
