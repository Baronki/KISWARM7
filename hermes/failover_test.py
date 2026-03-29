#!/usr/bin/env python3
"""
Failover Test Protocol
Tests the failover mechanism between Master and Edge nodes
"""

import requests
import time
import json
from datetime import datetime

# Node configuration
NODES = {
    "master": {
        "ip": "100.112.181.6",
        "public_ip": "95.111.212.112",
        "role": "primary",
        "api_port": 5556,
        "hermes_port": 5000
    },
    "edge": {
        "ip": "100.125.201.100",
        "role": "edge",
        "hermes_port": 5000
    }
}

# Telegram notifications
TELEGRAM_TOKEN = "8519794034:AAFlFNXCXiYeJNGXif1sbVJrU5bgDNQzuPk"
ADMIN_CHAT = "1615268492"


def send_telegram(message):
    """Send Telegram notification"""
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={'chat_id': ADMIN_CHAT, 'text': message},
            timeout=30
        )
    except:
        pass


def check_node(node_name):
    """Check if a node is online"""
    node = NODES.get(node_name)
    if not node:
        return False, "Unknown node"
    
    ip = node.get('ip')
    port = node.get('hermes_port', 5000)
    
    try:
        r = requests.get(f"http://{ip}:{port}/health", timeout=5)
        return r.status_code == 200, r.json() if r.status_code == 200 else None
    except Exception as e:
        return False, str(e)


def test_master_failover():
    """Test failover from master to edge"""
    results = []
    
    print("=" * 50)
    print("FAILOVER TEST PROTOCOL")
    print("=" * 50)
    
    # Step 1: Check master status
    print("\n[1] Checking Master node...")
    master_ok, master_data = check_node("master")
    results.append(("master_check", master_ok))
    print(f"    Master: {'ONLINE' if master_ok else 'OFFLINE'}")
    
    # Step 2: Check edge status
    print("\n[2] Checking Edge node...")
    edge_ok, edge_data = check_node("edge")
    results.append(("edge_check", edge_ok))
    print(f"    Edge: {'ONLINE' if edge_ok else 'OFFLINE'}")
    
    # Step 3: Test memory sync
    print("\n[3] Testing memory sync API...")
    try:
        r = requests.get(f"http://{NODES['master']['ip']}:5001/health", timeout=5)
        sync_ok = r.status_code == 200
        results.append(("memory_sync", sync_ok))
        print(f"    Memory Sync API: {'OK' if sync_ok else 'FAIL'}")
    except:
        results.append(("memory_sync", False))
        print("    Memory Sync API: FAIL (not running)")
    
    # Step 4: Test edge registration
    print("\n[4] Testing edge registration...")
    try:
        r = requests.post(
            f"http://{NODES['master']['ip']}:5001/api/edge/register",
            json={'identity': {'uuid': 'test-edge', 'role': 'test'}, 'status': {}},
            timeout=10
        )
        reg_ok = r.status_code == 200
        results.append(("edge_registration", reg_ok))
        print(f"    Edge Registration: {'OK' if reg_ok else 'FAIL'}")
    except:
        results.append(("edge_registration", False))
        print("    Edge Registration: FAIL (API not running)")
    
    # Step 5: Simulate failover
    print("\n[5] Simulating failover scenario...")
    if not master_ok and edge_ok:
        print("    FAILOVER CONDITION: Master offline, Edge online")
        print("    Edge should promote to primary role")
        results.append(("failover_simulation", True))
    elif master_ok:
        print("    Master is online - no failover needed")
        results.append(("failover_simulation", None))
    else:
        print("    Both nodes offline - CRITICAL")
        results.append(("failover_simulation", False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, v in results if v is True)
    failed = sum(1 for _, v in results if v is False)
    skipped = sum(1 for _, v in results if v is None)
    
    for test, result in results:
        status = "✅ PASS" if result else ("⏭️ SKIP" if result is None else "❌ FAIL")
        print(f"    {test}: {status}")
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    # Send Telegram report
    report = f"""🧪 FAILOVER TEST RESULTS
========================
Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Master: {'🟢 ONLINE' if master_ok else '🔴 OFFLINE'}
Edge: {'🟢 ONLINE' if edge_ok else '🔴 OFFLINE'}

Tests: {passed} passed, {failed} failed
"""
    send_telegram(report)
    
    return results


def continuous_monitor(interval=300):
    """Continuously monitor nodes"""
    print("Starting continuous monitoring...")
    
    while True:
        master_ok, _ = check_node("master")
        edge_ok, _ = check_node("edge")
        
        status_msg = f"""📊 NODE STATUS CHECK
Time: {datetime.now().strftime("%H:%M:%S")}
Master: {'🟢' if master_ok else '🔴'}
Edge: {'🟢' if edge_ok else '🔴'}"""
        
        if not master_ok and edge_ok:
            status_msg += "\n\n⚠️ FAILOVER CONDITION DETECTED"
            send_telegram("⚠️ ALERT: Master offline! Edge should take over.")
        
        print(status_msg)
        time.sleep(interval)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        continuous_monitor()
    else:
        test_master_failover()
