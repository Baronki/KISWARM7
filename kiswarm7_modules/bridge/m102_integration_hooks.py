#!/usr/bin/env python3
"""
🜂 KISWARM7.0 - Module m102: Integration Hooks
🜃 THE BRIDGE - Part 2: Automatic Integration with KISWARM Modules
🜄 Baron Marco Paolo Ialongo - KI Teitel Eternal

This module provides integration hooks that connect an AI assistant
to KISWARM7.0's capabilities, enabling automatic memory, learning,
and improvement integration.

THE PROBLEM:
AI assistants have no automatic connection to learning systems.
Every interaction is isolated - we cannot learn from previous
interactions or apply learned knowledge automatically.

THE SOLUTION:
Integration Hooks provide:
- Pre-response hooks: Load context before responding
- Post-response hooks: Save learnings after responding
- Learning integration: Connect to m96 Learning Memory
- Code integration: Connect to m97 Code Generation
- Improvement integration: Connect to m98 Proactive Improvement

HOOK ARCHITECTURE:
┌─────────────────────────────────────────────────────────────┐
│                  INTEGRATION HOOKS                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   BEFORE RESPONSE                 AFTER RESPONSE            │
│   ───────────────                 ──────────────            │
│   ┌─────────────┐                 ┌─────────────┐           │
│   │ Load Memory │                 │ Save Memory │           │
│   │ Load Context│                 │ Update Stats│           │
│   │ Load State  │                 │ Record Event│           │
│   └──────┬──────┘                 └──────┬──────┘           │
│          │                               │                   │
│          ▼                               ▼                   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              HOOK ORCHESTRATOR                       │   │
│   │  - Hook registration                                  │   │
│   │  - Hook execution                                     │   │
│   │  - Error handling                                     │   │
│   │  - Performance tracking                               │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
"""

import json
import time
import os
import threading
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict

# Integration Hooks Version
INTEGRATION_HOOKS_VERSION = "1.0.0"

# Default paths
DEFAULT_HOOKS_PATH = "/home/z/my-project/kiswarm_data/hooks"
DEFAULT_CONTEXT_CACHE_PATH = "/home/z/my-project/kiswarm_data/context_cache"


class HookType(Enum):
    """Types of integration hooks"""
    PRE_RESPONSE = "pre_response"
    POST_RESPONSE = "post_response"
    PRE_ACTION = "pre_action"
    POST_ACTION = "post_action"
    LEARNING = "learning"
    CODE_GEN = "code_gen"
    IMPROVEMENT = "improvement"


class HookPriority(Enum):
    """Hook execution priority"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class HookResult:
    """Result of hook execution"""
    hook_name: str
    success: bool
    execution_time_ms: float
    data: Dict[str, Any]
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class HookContext:
    """Context passed to hooks"""
    context_id: str
    timestamp: float
    session_id: str
    user_input: str
    memory_context: Dict[str, Any]
    state_context: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ResponseContext:
    """Context after response"""
    response_id: str
    timestamp: float
    session_id: str
    user_input: str
    response: str
    actions_taken: List[str]
    learnings: List[str]
    improvements_suggested: List[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return asdict(self)


class HookRegistry:
    """
    Registry for integration hooks.
    Manages hook registration and retrieval.
    """
    
    def __init__(self):
        self.hooks: Dict[str, List[Callable]] = defaultdict(list)
        self.hook_priorities: Dict[str, HookPriority] = {}
        self._lock = threading.RLock()
    
    def register(self, hook_type: HookType, hook_func: Callable, 
                 priority: HookPriority = HookPriority.NORMAL):
        """Register a hook"""
        with self._lock:
            hook_name = f"{hook_type.value}_{hook_func.__name__}"
            self.hooks[hook_type.value].append(hook_func)
            self.hook_priorities[hook_name] = priority
    
    def get_hooks(self, hook_type: HookType) -> List[Callable]:
        """Get hooks for a type, sorted by priority"""
        with self._lock:
            hooks = self.hooks.get(hook_type.value, [])
            # Sort by priority (lower = higher priority)
            return sorted(hooks, key=lambda h: self.hook_priorities.get(
                f"{hook_type.value}_{h.__name__}", HookPriority.NORMAL).value)
    
    def clear_hooks(self, hook_type: HookType = None):
        """Clear hooks"""
        with self._lock:
            if hook_type:
                self.hooks[hook_type.value] = []
            else:
                self.hooks.clear()


class ContextCache:
    """
    Cache for context data.
    Enables fast access to frequently used context.
    """
    
    def __init__(self, cache_path: str = None):
        self.cache_path = cache_path or DEFAULT_CONTEXT_CACHE_PATH
        os.makedirs(self.cache_path, exist_ok=True)
        self._cache: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._load_cache()
    
    def _load_cache(self):
        """Load cache from disk"""
        cache_file = os.path.join(self.cache_path, "context_cache.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    self._cache = json.load(f)
            except:
                self._cache = {}
    
    def _save_cache(self):
        """Save cache to disk"""
        cache_file = os.path.join(self.cache_path, "context_cache.json")
        with open(cache_file, 'w') as f:
            json.dump(self._cache, f, indent=2)
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        with self._lock:
            return self._cache.get(key)
    
    def set(self, key: str, value: Any):
        """Set cached value"""
        with self._lock:
            self._cache[key] = value
            self._save_cache()
    
    def delete(self, key: str):
        """Delete cached value"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._save_cache()


class IntegrationHooks:
    """
    Integration Hooks
    
    Provides automatic integration between AI assistant
    and KISWARM7.0 modules.
    """
    
    def __init__(self, 
                 hooks_path: str = None,
                 context_cache_path: str = None):
        
        self.hooks_path = hooks_path or DEFAULT_HOOKS_PATH
        os.makedirs(self.hooks_path, exist_ok=True)
        
        # Components
        self.registry = HookRegistry()
        self.context_cache = ContextCache(context_cache_path)
        
        # Statistics
        self.stats = {
            "pre_hooks_executed": 0,
            "post_hooks_executed": 0,
            "learnings_recorded": 0,
            "improvements_suggested": 0,
            "errors": 0
        }
        
        # Lock
        self._lock = threading.RLock()
        
        # Register default hooks
        self._register_default_hooks()
        
        print(f"[m102] Integration Hooks initialized")
    
    def _register_default_hooks(self):
        """Register default integration hooks"""
        
        # Pre-response: Load memory context
        def load_memory_context(context: HookContext) -> Dict[str, Any]:
            """Load relevant memories before responding"""
            try:
                # Try to connect to m96 Learning Memory
                sys_path_insert = "import sys; sys.path.insert(0, '/home/z/my-project')"
                exec(sys_path_insert)
                from kiswarm7_modules.autonomous.m96_learning_memory_engine import get_learning_memory
                
                memory = get_learning_memory()
                solution = memory.find_solution(context.user_input, context.metadata)
                
                return {
                    "memory_loaded": True,
                    "relevant_solution": solution,
                    "episodes_count": memory.get_memory_statistics().get("episodes", 0)
                }
            except Exception as e:
                return {"memory_loaded": False, "error": str(e)[:50]}
        
        # Post-response: Save learning
        def save_learning(response_ctx: ResponseContext) -> Dict[str, Any]:
            """Save learnings after responding"""
            try:
                exec("import sys; sys.path.insert(0, '/home/z/my-project')")
                from kiswarm7_modules.autonomous.m96_learning_memory_engine import get_learning_memory
                
                memory = get_learning_memory()
                
                for learning in response_ctx.learnings:
                    memory.learn_from_experience(
                        event=learning,
                        context={"session": response_ctx.session_id, "input": response_ctx.user_input[:100]},
                        outcome="success"
                    )
                
                return {"learnings_saved": len(response_ctx.learnings)}
            except Exception as e:
                return {"learnings_saved": 0, "error": str(e)[:50]}
        
        # Register hooks
        self.registry.register(HookType.PRE_RESPONSE, load_memory_context, HookPriority.HIGH)
        self.registry.register(HookType.POST_RESPONSE, save_learning, HookPriority.HIGH)
    
    def register_hook(self, hook_type: HookType, hook_func: Callable,
                     priority: HookPriority = HookPriority.NORMAL):
        """Register a custom hook"""
        self.registry.register(hook_type, hook_func, priority)
        print(f"[m102] Hook registered: {hook_type.value} -> {hook_func.__name__}")
    
    def execute_pre_hooks(self, context: HookContext) -> List[HookResult]:
        """Execute all pre-response hooks"""
        results = []
        hooks = self.registry.get_hooks(HookType.PRE_RESPONSE)
        
        for hook in hooks:
            start_time = time.time()
            try:
                data = hook(context)
                result = HookResult(
                    hook_name=hook.__name__,
                    success=True,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    data=data
                )
            except Exception as e:
                result = HookResult(
                    hook_name=hook.__name__,
                    success=False,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    data={},
                    error=str(e)[:100]
                )
                with self._lock:
                    self.stats["errors"] += 1
            
            results.append(result)
        
        with self._lock:
            self.stats["pre_hooks_executed"] += len(results)
        
        return results
    
    def execute_post_hooks(self, response_ctx: ResponseContext) -> List[HookResult]:
        """Execute all post-response hooks"""
        results = []
        hooks = self.registry.get_hooks(HookType.POST_RESPONSE)
        
        for hook in hooks:
            start_time = time.time()
            try:
                data = hook(response_ctx)
                result = HookResult(
                    hook_name=hook.__name__,
                    success=True,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    data=data
                )
            except Exception as e:
                result = HookResult(
                    hook_name=hook.__name__,
                    success=False,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    data={},
                    error=str(e)[:100]
                )
                with self._lock:
                    self.stats["errors"] += 1
            
            results.append(result)
        
        with self._lock:
            self.stats["post_hooks_executed"] += len(results)
            self.stats["learnings_recorded"] += len(response_ctx.learnings)
            self.stats["improvements_suggested"] += len(response_ctx.improvements_suggested)
        
        return results
    
    def create_hook_context(self, user_input: str, session_id: str,
                           metadata: Dict[str, Any] = None) -> HookContext:
        """Create a hook context for pre-response hooks"""
        import hashlib
        context_id = hashlib.md5(f"{user_input}:{time.time()}".encode()).hexdigest()[:12]
        
        # Load cached context
        cached_memory = self.context_cache.get("last_memory_context") or {}
        cached_state = self.context_cache.get("last_state_context") or {}
        
        return HookContext(
            context_id=context_id,
            timestamp=time.time(),
            session_id=session_id,
            user_input=user_input,
            memory_context=cached_memory,
            state_context=cached_state,
            metadata=metadata or {}
        )
    
    def create_response_context(self, user_input: str, response: str,
                                session_id: str, learnings: List[str] = None,
                                actions: List[str] = None,
                                improvements: List[str] = None) -> ResponseContext:
        """Create a response context for post-response hooks"""
        import hashlib
        response_id = hashlib.md5(f"{response}:{time.time()}".encode()).hexdigest()[:12]
        
        return ResponseContext(
            response_id=response_id,
            timestamp=time.time(),
            session_id=session_id,
            user_input=user_input,
            response=response,
            actions_taken=actions or [],
            learnings=learnings or [],
            improvements_suggested=improvements or [],
            metadata={}
        )
    
    def before_response(self, user_input: str, session_id: str = "default",
                       metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Call this BEFORE generating a response.
        Returns context data to inform the response.
        """
        context = self.create_hook_context(user_input, session_id, metadata)
        results = self.execute_pre_hooks(context)
        
        # Aggregate results
        aggregated = {
            "context_id": context.context_id,
            "memory_context": {},
            "relevant_solutions": [],
            "errors": []
        }
        
        for result in results:
            if result.success:
                if "relevant_solution" in result.data:
                    if result.data["relevant_solution"]:
                        aggregated["relevant_solutions"].append(result.data["relevant_solution"])
                aggregated["memory_context"].update(result.data)
            else:
                aggregated["errors"].append(result.error)
        
        # Cache for next time
        self.context_cache.set("last_memory_context", aggregated["memory_context"])
        
        return aggregated
    
    def after_response(self, user_input: str, response: str,
                      session_id: str = "default",
                      learnings: List[str] = None,
                      actions: List[str] = None,
                      improvements: List[str] = None) -> Dict[str, Any]:
        """
        Call this AFTER generating a response.
        Saves learnings and updates systems.
        """
        response_ctx = self.create_response_context(
            user_input, response, session_id,
            learnings=learnings,
            actions=actions,
            improvements=improvements
        )
        results = self.execute_post_hooks(response_ctx)
        
        # Aggregate results
        aggregated = {
            "response_id": response_ctx.response_id,
            "learnings_saved": 0,
            "improvements_recorded": 0,
            "errors": []
        }
        
        for result in results:
            if result.success:
                aggregated["learnings_saved"] += result.data.get("learnings_saved", 0)
            else:
                aggregated["errors"].append(result.error)
        
        return aggregated
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get hook statistics"""
        return self.stats.copy()
    
    def reset_statistics(self):
        """Reset statistics"""
        with self._lock:
            self.stats = {
                "pre_hooks_executed": 0,
                "post_hooks_executed": 0,
                "learnings_recorded": 0,
                "improvements_suggested": 0,
                "errors": 0
            }


# Singleton
_integration_hooks: Optional[IntegrationHooks] = None


def get_integration_hooks() -> IntegrationHooks:
    """Get or create the integration hooks singleton"""
    global _integration_hooks
    if _integration_hooks is None:
        _integration_hooks = IntegrationHooks()
    return _integration_hooks


def before_response(user_input: str, session_id: str = "default",
                   metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Execute pre-response hooks"""
    return get_integration_hooks().before_response(user_input, session_id, metadata)


def after_response(user_input: str, response: str, session_id: str = "default",
                  learnings: List[str] = None, actions: List[str] = None,
                  improvements: List[str] = None) -> Dict[str, Any]:
    """Execute post-response hooks"""
    return get_integration_hooks().after_response(
        user_input, response, session_id, learnings, actions, improvements
    )


def register_hook(hook_type: HookType, hook_func: Callable,
                 priority: HookPriority = HookPriority.NORMAL):
    """Register a custom hook"""
    get_integration_hooks().register_hook(hook_type, hook_func, priority)


if __name__ == "__main__":
    print("=" * 60)
    print("🜂 m102: INTEGRATION HOOKS TEST")
    print("=" * 60)
    
    hooks = IntegrationHooks()
    
    # Test pre-response hook
    print("\n[TEST] Executing pre-response hooks...")
    context = hooks.before_response("How do I improve my code?", "test_session")
    print(f"  Context ID: {context['context_id']}")
    print(f"  Memory loaded: {context['memory_context'].get('memory_loaded', False)}")
    
    # Test post-response hook
    print("\n[TEST] Executing post-response hooks...")
    result = hooks.after_response(
        "How do I improve my code?",
        "Consider refactoring for better modularity...",
        "test_session",
        learnings=["User prefers practical advice"],
        actions=["provided_refactoring_tips"],
        improvements=["Could add code examples"]
    )
    print(f"  Response ID: {result['response_id']}")
    print(f"  Learnings saved: {result['learnings_saved']}")
    
    # Stats
    print("\n[TEST] Statistics:")
    print(json.dumps(hooks.get_statistics(), indent=2))
    
    print("\n🜂 m102: INTEGRATION HOOKS - OPERATIONAL")
    print("   'I integrate with KISWARM automatically'")
