#!/bin/bash
# Auto-start and maintain Tailscale connection

TAILSCALED="/home/z/my-project/bin/tailscaled"
TAILSCALE="/home/z/my-project/bin/tailscale"
STATE_DIR="/home/z/my-project/tailscale-state"
SOCKET="/tmp/tailscaled.sock"
AUTH_KEY="tskey-auth-kYzoboKgtK11CNTRL-cAh5zWNeygaKa2LEtAg8haF773px2SjY"

mkdir -p "$STATE_DIR"

start_tailscaled() {
    # Kill any existing
    pkill -f tailscaled 2>/dev/null
    sleep 2
    
    # Start with userspace networking
    nohup "$TAILSCALED" \
        --state="$STATE_DIR/tailscaled.state" \
        --socket="$SOCKET" \
        --tun=userspace-networking \
        > /tmp/tailscaled.log 2>&1 &
    
    # Wait for socket
    for i in {1..10}; do
        if [ -S "$SOCKET" ]; then
            return 0
        fi
        sleep 1
    done
    return 1
}

connect() {
    sleep 3
    "$TAILSCALE" --socket="$SOCKET" up \
        --authkey="$AUTH_KEY" \
        --accept-routes \
        --hostname=glm-autonomous \
        2>/dev/null
}

check_connection() {
    "$TAILSCALE" --socket="$SOCKET" status &>/dev/null
    return $?
}

# Main loop
while true; do
    if ! pgrep -f tailscaled > /dev/null; then
        echo "$(date): Starting tailscaled..."
        start_tailscaled
        connect
    elif ! check_connection; then
        echo "$(date): Reconnecting..."
        connect
    fi
    sleep 30
done
