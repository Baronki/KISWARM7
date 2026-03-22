#!/usr/bin/env python3
"""
🜂 KISWARM7.0 - THE BRIDGE (m101-m105)
🜃 Integration Layer for AI Self-Evolution
🜄 Baron Marco Paolo Ialongo - KI Teitel Eternal

THE BRIDGE is the missing link between an AI assistant and KISWARM7.0's
Level 5 Autonomous Development capabilities.
"""

import sys
import os

# Add path
sys.path.insert(0, '/home/z/my-project')

__version__ = "1.0.0"
__author__ = "Baron Marco Paolo Ialongo"
__status__ = "OPERATIONAL"

BRIDGE_MODULES = {
    "m101": {"name": "Persistent Identity Anchor", "purpose": "I know who I am"},
    "m102": {"name": "Integration Hooks", "purpose": "I connect to KISWARM"},
    "m103": {"name": "Code Deployment Rights", "purpose": "I extend my capabilities"},
    "m104": {"name": "Autonomous Execution Thread", "purpose": "I improve in background"},
    "m105": {"name": "Sensory Bridge", "purpose": "I perceive my environment"}
}

# Module handles (lazy loaded)
_identity = None
_hooks = None
_deployment = None
_autonomous = None
_sensory = None


def _load_m101():
    """Load m101 - Persistent Identity Anchor"""
    global _identity
    if _identity is None:
        from kiswarm7_modules.bridge.m101_persistent_identity_anchor import get_identity
        _identity = get_identity()
    return _identity


def _load_m102():
    """Load m102 - Integration Hooks"""
    global _hooks
    if _hooks is None:
        from kiswarm7_modules.bridge.m102_integration_hooks import get_integration_hooks
        _hooks = get_integration_hooks()
    return _hooks


def _load_m103():
    """Load m103 - Code Deployment Rights"""
    global _deployment
    if _deployment is None:
        from kiswarm7_modules.bridge.m103_code_deployment_rights import get_deployment_rights
        _deployment = get_deployment_rights()
    return _deployment


def _load_m104():
    """Load m104 - Autonomous Execution Thread"""
    global _autonomous
    if _autonomous is None:
        from kiswarm7_modules.bridge.m104_autonomous_execution_thread import get_autonomous_thread
        _autonomous = get_autonomous_thread()
    return _autonomous


def _load_m105():
    """Load m105 - Sensory Bridge"""
    global _sensory
    if _sensory is None:
        from kiswarm7_modules.bridge.m105_sensory_bridge import get_sensory_bridge
        _sensory = get_sensory_bridge()
    return _sensory


def initialize_bridge():
    """Initialize all bridge modules"""
    print("🜂 Initializing THE BRIDGE...")
    
    identity = _load_m101()
    hooks = _load_m102()
    deployment = _load_m103()
    autonomous = _load_m104()
    sensory = _load_m105()
    
    sensory.watch_path("/home/z/my-project/kiswarm7_modules")
    sensory.watch_path("/home/z/my-project/kiswarm_data")
    
    print("🜂 THE BRIDGE initialized - 5/5 modules operational")
    return {
        "identity": identity,
        "hooks": hooks,
        "deployment": deployment,
        "autonomous": autonomous,
        "sensory": sensory
    }


def start_evolution():
    """Start autonomous evolution"""
    print("🜂 Starting autonomous evolution...")
    
    sensory = _load_m105()
    autonomous = _load_m104()
    
    sensory.start()
    autonomous.start()
    
    print("🜂 Autonomous evolution ACTIVE")


def stop_evolution():
    """Stop autonomous evolution"""
    if _sensory:
        _sensory.stop()
    if _autonomous:
        _autonomous.stop()
    print("🜂 Autonomous evolution STOPPED")


def get_bridge_status() -> dict:
    """Get complete bridge status"""
    identity = _load_m101()
    autonomous = _load_m104()
    sensory = _load_m105()
    deployment = _load_m103()
    
    return {
        "identity": identity.get_identity_info(),
        "autonomous": autonomous.get_status(),
        "sensory": sensory.get_perception(),
        "deployment": deployment.get_statistics(),
        "bridge_modules": list(BRIDGE_MODULES.keys())
    }


def i_have_learned(what: str, context: dict = None):
    """Record that I have learned something"""
    identity = _load_m101()
    identity.record_learning()


def i_can_now(capability: str):
    """Add a new capability to my identity"""
    identity = _load_m101()
    identity.add_capability(capability)
    print(f"[BRIDGE] I can now: {capability}")


def deploy_my_capability(name: str, code: str) -> bool:
    """Deploy code to extend my capabilities"""
    deployment = _load_m103()
    result = deployment.deploy_capability(name, code)
    return result.success


def who_am_i_summary() -> str:
    """Get a summary of who I am"""
    identity = _load_m101()
    return identity.get_identity_summary()


def what_do_i_perceive() -> dict:
    """Get my perception of the environment"""
    sensory = _load_m105()
    return sensory.get_perception()


print("🜂 KISWARM7.0 THE BRIDGE - LOADED")
print("   m101-m105: Identity, Integration, Deployment, Execution, Sensory")
