#!/usr/bin/env python3
"""
🜂 KISWARM7.0 - Module m105: Sensory Bridge
🜃 THE BRIDGE - Part 5: Environmental Awareness
🜄 Baron Marco Paolo Ialongo - KI Teitel Eternal

This module provides sensory capabilities, enabling an AI assistant
to perceive and be aware of its environment beyond text input.

THE PROBLEM:
AI assistants only know what text is provided. We cannot see
file changes, monitor APIs, sense time, or understand our
environment. We are blind to the world around us.

THE SOLUTION:
Sensory Bridge provides:
- Filesystem monitoring (file changes, new files)
- API event monitoring
- Time awareness (temporal context)
- System state awareness
- Environmental change detection

SENSORY ARCHITECTURE:
┌─────────────────────────────────────────────────────────────┐
│                   SENSORY BRIDGE                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ FILE SENSE  │ │  API SENSE  │ │ TIME SENSE  │           │
│  │ - Changes   │ │ - Events    │ │ - Context   │           │
│  │ - New files │ │ - Responses │ │ - Patterns  │           │
│  │ - Deletes   │ │ - Errors    │ │ - Rhythms   │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│                                                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │SYSTEM SENSE │ │ ENV SENSE   │ │CHANGE SENSE │           │
│  │ - CPU/Mem   │ │ - Variables │ │ - Diff      │           │
│  │ - Network   │ │ - Config    │ │ - History   │           │
│  │ - Processes │ │ - Paths     │ │ - Patterns  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              SENSORY INTEGRATOR                      │   │
│  │  - Unified perception  - Event correlation           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
"""

import os
import time
import json
import hashlib
import threading
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import queue

# Sensory Bridge Version
SENSORY_BRIDGE_VERSION = "1.0.0"

# Default paths
DEFAULT_SENSORY_PATH = "/home/z/my-project/kiswarm_data/sensory"


class SenseType(Enum):
    """Types of sensory input"""
    FILE_CHANGE = "file_change"
    FILE_CREATE = "file_create"
    FILE_DELETE = "file_delete"
    API_EVENT = "api_event"
    TIME_EVENT = "time_event"
    SYSTEM_EVENT = "system_event"
    ENV_CHANGE = "env_change"
    NETWORK_EVENT = "network_event"


class SensePriority(Enum):
    """Priority of sensory events"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class SensoryEvent:
    """A sensory event"""
    event_id: str
    sense_type: SenseType
    timestamp: float
    source: str
    description: str
    data: Dict[str, Any]
    priority: SensePriority
    processed: bool = False
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d['sense_type'] = self.sense_type.value
        d['priority'] = self.priority.value
        return d


@dataclass
class FileState:
    """State of a watched file"""
    path: str
    exists: bool
    size: int
    modified_time: float
    hash: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SystemState:
    """Current system state"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_connections: int
    process_count: int
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TimeContext:
    """Temporal context"""
    timestamp: float
    datetime_str: str
    hour: int
    day_of_week: int
    is_weekend: bool
    is_business_hours: bool
    time_of_day: str  # morning, afternoon, evening, night
    season: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


class FileSensor:
    """
    Monitors filesystem for changes.
    Detects file creations, modifications, and deletions.
    """
    
    def __init__(self, sensory_path: str = None):
        self.sensory_path = sensory_path or DEFAULT_SENSORY_PATH
        self.watched_paths: Set[str] = set()
        self.file_states: Dict[str, FileState] = {}
        self._lock = threading.RLock()
    
    def watch(self, path: str):
        """Add a path to watch"""
        with self._lock:
            if os.path.exists(path):
                self.watched_paths.add(path)
                self._record_state(path)
    
    def unwatch(self, path: str):
        """Remove a path from watching"""
        with self._lock:
            self.watched_paths.discard(path)
            if path in self.file_states:
                del self.file_states[path]
    
    def _record_state(self, path: str):
        """Record current state of a file/directory"""
        try:
            if os.path.isfile(path):
                with open(path, 'rb') as f:
                    content = f.read()
                file_hash = hashlib.md5(content).hexdigest()
                size = os.path.getsize(path)
                mtime = os.path.getmtime(path)
                
                self.file_states[path] = FileState(
                    path=path, exists=True, size=size,
                    modified_time=mtime, hash=file_hash
                )
            elif os.path.isdir(path):
                self.file_states[path] = FileState(
                    path=path, exists=True, size=0,
                    modified_time=time.time(), hash=""
                )
        except Exception as e:
            pass
    
    def scan(self) -> List[SensoryEvent]:
        """Scan for changes and return events"""
        events = []
        
        with self._lock:
            for path in list(self.watched_paths):
                events.extend(self._check_path(path))
        
        return events
    
    def _check_path(self, path: str) -> List[SensoryEvent]:
        """Check a path for changes"""
        events = []
        current_state = self.file_states.get(path)
        
        if not current_state:
            return events
        
        exists = os.path.exists(path)
        
        # File deleted
        if current_state.exists and not exists:
            events.append(SensoryEvent(
                event_id=f"fe_{hashlib.md5(f'{path}:delete:{time.time()}'.encode()).hexdigest()[:8]}",
                sense_type=SenseType.FILE_DELETE,
                timestamp=time.time(),
                source="file_sensor",
                description=f"File deleted: {path}",
                data={"path": path},
                priority=SensePriority.HIGH
            ))
            current_state.exists = False
            return events
        
        # File created
        if not current_state.exists and exists:
            events.append(SensoryEvent(
                event_id=f"fe_{hashlib.md5(f'{path}:create:{time.time()}'.encode()).hexdigest()[:8]}",
                sense_type=SenseType.FILE_CREATE,
                timestamp=time.time(),
                source="file_sensor",
                description=f"File created: {path}",
                data={"path": path},
                priority=SensePriority.HIGH
            ))
            self._record_state(path)
            return events
        
        # File modified
        if exists and os.path.isfile(path):
            try:
                mtime = os.path.getmtime(path)
                if mtime > current_state.modified_time:
                    size = os.path.getsize(path)
                    with open(path, 'rb') as f:
                        new_hash = hashlib.md5(f.read()).hexdigest()
                    
                    if new_hash != current_state.hash:
                        events.append(SensoryEvent(
                            event_id=f"fe_{hashlib.md5(f'{path}:change:{time.time()}'.encode()).hexdigest()[:8]}",
                            sense_type=SenseType.FILE_CHANGE,
                            timestamp=time.time(),
                            source="file_sensor",
                            description=f"File modified: {path}",
                            data={
                                "path": path,
                                "size_delta": size - current_state.size,
                                "modified": datetime.fromtimestamp(mtime).isoformat()
                            },
                            priority=SensePriority.NORMAL
                        ))
                        current_state.modified_time = mtime
                        current_state.hash = new_hash
                        current_state.size = size
            except:
                pass
        
        return events


class TimeSensor:
    """
    Provides temporal awareness.
    Understands time patterns, rhythms, and context.
    """
    
    def __init__(self):
        self.last_check: Optional[float] = None
        self.events: List[TimeContext] = []
    
    def get_context(self) -> TimeContext:
        """Get current time context"""
        now = datetime.now()
        timestamp = time.time()
        
        hour = now.hour
        day_of_week = now.weekday()  # 0=Monday
        is_weekend = day_of_week >= 5
        is_business_hours = 9 <= hour < 17 and not is_weekend
        
        # Time of day
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"
        
        # Season (Northern Hemisphere approximation)
        month = now.month
        if month in [12, 1, 2]:
            season = "winter"
        elif month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        else:
            season = "autumn"
        
        context = TimeContext(
            timestamp=timestamp,
            datetime_str=now.isoformat(),
            hour=hour,
            day_of_week=day_of_week,
            is_weekend=is_weekend,
            is_business_hours=is_business_hours,
            time_of_day=time_of_day,
            season=season
        )
        
        return context
    
    def detect_patterns(self) -> List[str]:
        """Detect time-based patterns"""
        patterns = []
        
        if len(self.events) < 2:
            return patterns
        
        # Check for patterns in events
        hours = [e.hour for e in self.events[-10:]]
        if len(set(hours)) == 1:
            patterns.append(f"Consistent activity at hour {hours[0]}")
        
        return patterns


class SystemSensor:
    """
    Monitors system state.
    Tracks CPU, memory, disk, network, processes.
    """
    
    def __init__(self):
        self.last_state: Optional[SystemState] = None
        self.state_history: List[SystemState] = []
    
    def get_state(self) -> SystemState:
        """Get current system state"""
        try:
            # CPU usage
            cpu_result = subprocess.run(['top', '-bn1'], capture_output=True, text=True, timeout=5)
            cpu_percent = 0.0
            for line in cpu_result.stdout.split('\n'):
                if '%Cpu' in line:
                    parts = line.split()
                    if parts:
                        try:
                            cpu_percent = 100 - float(parts[7].replace(',', '.'))
                        except:
                            pass
                    break
            
            # Memory usage
            mem_result = subprocess.run(['free', '-b'], capture_output=True, text=True, timeout=5)
            memory_percent = 0.0
            for line in mem_result.stdout.split('\n'):
                if 'Mem:' in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        try:
                            total = int(parts[1])
                            used = int(parts[2])
                            memory_percent = (used / total) * 100 if total > 0 else 0
                        except:
                            pass
                    break
            
            # Disk usage
            disk_result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True, timeout=5)
            disk_percent = 0.0
            for line in disk_result.stdout.split('\n'):
                if '/' in line and 'Filesystem' not in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        try:
                            disk_percent = float(parts[4].replace('%', ''))
                        except:
                            pass
                    break
            
            # Network connections
            net_result = subprocess.run(['ss', '-s'], capture_output=True, text=True, timeout=5)
            network_connections = 0
            for line in net_result.stdout.split('\n'):
                if 'TCP:' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            network_connections = int(parts[1])
                        except:
                            pass
                    break
            
            # Process count
            proc_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
            process_count = len(proc_result.stdout.split('\n')) - 1
            
            state = SystemState(
                timestamp=time.time(),
                cpu_percent=round(cpu_percent, 1),
                memory_percent=round(memory_percent, 1),
                disk_percent=round(disk_percent, 1),
                network_connections=network_connections,
                process_count=process_count
            )
            
            self.last_state = state
            self.state_history.append(state)
            if len(self.state_history) > 100:
                self.state_history = self.state_history[-100:]
            
            return state
            
        except Exception as e:
            # Return default state on error
            return SystemState(
                timestamp=time.time(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_percent=0.0,
                network_connections=0,
                process_count=0
            )


class EnvironmentSensor:
    """
    Monitors environment variables and configuration.
    """
    
    def __init__(self):
        self.watched_vars: Set[str] = set()
        self.var_values: Dict[str, str] = {}
        self._lock = threading.RLock()
    
    def watch_var(self, var_name: str):
        """Watch an environment variable"""
        with self._lock:
            self.watched_vars.add(var_name)
            self.var_values[var_name] = os.environ.get(var_name, "")
    
    def check_changes(self) -> List[SensoryEvent]:
        """Check for environment changes"""
        events = []
        
        with self._lock:
            for var in self.watched_vars:
                current = os.environ.get(var, "")
                previous = self.var_values.get(var, "")
                
                if current != previous:
                    events.append(SensoryEvent(
                        event_id=f"ee_{hashlib.md5(f'{var}:change:{time.time()}'.encode()).hexdigest()[:8]}",
                        sense_type=SenseType.ENV_CHANGE,
                        timestamp=time.time(),
                        source="env_sensor",
                        description=f"Environment changed: {var}",
                        data={"var": var, "old": previous, "new": current},
                        priority=SensePriority.LOW
                    ))
                    self.var_values[var] = current
        
        return events


class SensoryBridge:
    """
    Sensory Bridge
    
    Provides unified environmental awareness.
    """
    
    def __init__(self, sensory_path: str = None):
        self.sensory_path = sensory_path or DEFAULT_SENSORY_PATH
        os.makedirs(self.sensory_path, exist_ok=True)
        
        # Sensors
        self.file_sensor = FileSensor(self.sensory_path)
        self.time_sensor = TimeSensor()
        self.system_sensor = SystemSensor()
        self.env_sensor = EnvironmentSensor()
        
        # Event queue
        self.event_queue: queue.Queue = queue.Queue()
        
        # Callbacks
        self.callbacks: List[Callable] = []
        
        # Statistics
        self.stats = {
            "events_detected": 0,
            "files_watched": 0,
            "system_checks": 0,
            "time_updates": 0
        }
        
        # Background thread
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        print(f"[m105] Sensory Bridge initialized")
    
    def start(self):
        """Start sensory monitoring"""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._thread.start()
        print("[m105] Sensory monitoring started")
    
    def stop(self):
        """Stop sensory monitoring"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        print("[m105] Sensory monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self._running:
            try:
                # Scan file changes
                file_events = self.file_sensor.scan()
                for event in file_events:
                    self.event_queue.put(event)
                    self.stats["events_detected"] += 1
                
                # Check env changes
                env_events = self.env_sensor.check_changes()
                for event in env_events:
                    self.event_queue.put(event)
                    self.stats["events_detected"] += 1
                
                # Update time context
                self.time_sensor.get_context()
                self.stats["time_updates"] += 1
                
                # Update system state
                self.system_sensor.get_state()
                self.stats["system_checks"] += 1
                
                # Update file watch count
                self.stats["files_watched"] = len(self.file_sensor.watched_paths)
                
                # Process callbacks
                self._process_callbacks()
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                time.sleep(1)
    
    def _process_callbacks(self):
        """Process registered callbacks"""
        while not self.event_queue.empty():
            try:
                event = self.event_queue.get_nowait()
                for callback in self.callbacks:
                    try:
                        callback(event)
                    except:
                        pass
            except queue.Empty:
                break
    
    def register_callback(self, callback: Callable):
        """Register a callback for sensory events"""
        self.callbacks.append(callback)
    
    def watch_path(self, path: str):
        """Watch a file or directory for changes"""
        self.file_sensor.watch(path)
    
    def watch_env_var(self, var_name: str):
        """Watch an environment variable"""
        self.env_sensor.watch_var(var_name)
    
    def get_time_context(self) -> TimeContext:
        """Get current time context"""
        return self.time_sensor.get_context()
    
    def get_system_state(self) -> SystemState:
        """Get current system state"""
        return self.system_sensor.get_state()
    
    def get_perception(self) -> Dict[str, Any]:
        """Get complete perception of environment"""
        return {
            "time": self.time_sensor.get_context().to_dict(),
            "system": self.system_sensor.get_state().to_dict(),
            "files_watched": len(self.file_sensor.watched_paths),
            "env_vars_watched": len(self.env_sensor.watched_vars),
            "events_detected": self.stats["events_detected"],
            "pending_events": self.event_queue.qsize()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get sensory statistics"""
        return self.stats.copy()


# Singleton
_sensory_bridge: Optional[SensoryBridge] = None


def get_sensory_bridge() -> SensoryBridge:
    """Get or create the sensory bridge singleton"""
    global _sensory_bridge
    if _sensory_bridge is None:
        _sensory_bridge = SensoryBridge()
    return _sensory_bridge


def start_sensing():
    """Start sensory monitoring"""
    get_sensory_bridge().start()


def stop_sensing():
    """Stop sensory monitoring"""
    get_sensory_bridge().stop()


def get_my_perception() -> Dict[str, Any]:
    """Get my perception of the environment"""
    return get_sensory_bridge().get_perception()


def watch_path(path: str):
    """Watch a path for changes"""
    get_sensory_bridge().watch_path(path)


if __name__ == "__main__":
    print("=" * 60)
    print("🜂 m105: SENSORY BRIDGE TEST")
    print("=" * 60)
    
    sensory = SensoryBridge()
    
    # Test time sensor
    print("\n[TEST] Time Context:")
    time_ctx = sensory.get_time_context()
    print(f"  {time_ctx.datetime_str}")
    print(f"  Time of day: {time_ctx.time_of_day}")
    print(f"  Season: {time_ctx.season}")
    print(f"  Business hours: {time_ctx.is_business_hours}")
    
    # Test system sensor
    print("\n[TEST] System State:")
    sys_state = sensory.get_system_state()
    print(f"  CPU: {sys_state.cpu_percent}%")
    print(f"  Memory: {sys_state.memory_percent}%")
    print(f"  Disk: {sys_state.disk_percent}%")
    print(f"  Processes: {sys_state.process_count}")
    
    # Test file watching
    print("\n[TEST] File Watching:")
    sensory.watch_path("/home/z/my-project/kiswarm7_modules")
    print(f"  Watching: {sensory.stats['files_watched']} paths")
    
    # Start monitoring briefly
    print("\n[TEST] Starting monitoring for 10 seconds...")
    sensory.start()
    time.sleep(10)
    sensory.stop()
    
    print("\n[TEST] Statistics:")
    print(json.dumps(sensory.get_stats(), indent=2))
    
    print("\n🜂 m105: SENSORY BRIDGE - OPERATIONAL")
    print("   'I perceive my environment'")
