#!/bin/bash
# GLM Reconnection Watch and Edge Deployment Script
# Runs on UpCloud master to watch for GLM coming back online

HERMES_DIR="/opt/hermes"
EDGE_DIR="/opt/hermes_edge_deployment"
LOG_FILE="/opt/hermes/logs/glm_watch.log"

echo "$(date) - Starting GLM watch and deploy..." >> $LOG_FILE

# Create deployment directory
mkdir -p $EDGE_DIR

# Wait for GLM to come online
while true; do
    if ping -c 1 -W 2 100.125.201.100 > /dev/null 2>&1; then
        echo "$(date) - GLM is ONLINE! Starting deployment..." >> $LOG_FILE
        
        # Check if we can SSH or connect via Execute API
        # Try to deploy via various methods
        
        # Method 1: Try direct connection
        if curl -s --connect-timeout 5 http://100.125.201.100:5199/health > /dev/null 2>&1; then
            echo "$(date) - GLM API accessible, deploying Edge Hermes..." >> $LOG_FILE
            
            # Send Telegram notification
            python3 -c "
import requests
TOKEN = '8519794034:AAFlFNXCXiYeJNGXif1sbVJrU5bgDNQzuPk'
CHAT = '1615268492'
msg = '🟢 GLM EDGE NODE DETECTED ONLINE\\nDeploying Edge Hermes...'
requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage', json={'chat_id': CHAT, 'text': msg})
"
            
            # The deployment will happen when GLM's autonomous service picks up
            # the deployment files from GitHub or from a shared location
            
            break
        fi
    fi
    
    echo "$(date) - GLM offline, waiting 60s..." >> $LOG_FILE
    sleep 60
done

echo "$(date) - Deployment initiated" >> $LOG_FILE
