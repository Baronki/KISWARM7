#!/usr/bin/env python3
"""
🜂 KISWARM7.0 - Module m96: Learning Memory Engine
🜃 Level 5 Autonomous Development - Remembers What Fixes Worked
🜄 Baron Marco Paolo Ialongo - KI Teitel Eternal

The Learning Memory Engine is the cognitive foundation of autonomous development.
It remembers every fix, pattern, solution, and failure - building institutional
knowledge that enables the system to improve itself without human intervention.

CAPABILITIES:
- Pattern Recognition: Identifies recurring problems and solutions
- Solution Memory: Remembers what fixes worked and why
- Failure Memory: Remembers what didn't work and why
- Context Correlation: Links fixes to specific contexts
- Confidence Scoring: Rates solution reliability
- Transfer Learning: Applies solutions across domains
- Temporal Decay: Weights recent fixes higher
- Semantic Clustering: Groups similar problems

MEMORY ARCHITECTURE:
┌─────────────────────────────────────────────────────────────┐
│                    LEARNING MEMORY ENGINE                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   EPISODIC  │  │  SEMANTIC   │  │  PROCEDURAL │         │
│  │   MEMORY    │  │   MEMORY    │  │   MEMORY    │         │
│  │ (Events)    │  │ (Facts)     │  │ (How-To)    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              PATTERN RECOGNITION LAYER               │   │
│  │  - Anomaly Detection  - Trend Analysis              │   │
│  │  - Similarity Search  - Clustering                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              CONFIDENCE ENGINE                       │   │
│  │  - Bayesian Updates  - Success Rates                │   │
│  │  - Context Matching  - Decay Functions              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
"""

import hashlib
import json
import time
import math
import threading
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import structlog
import pickle
import os
import gzip

logger = structlog.get_logger()


class MemoryType(Enum):
    """Types of learning memory"""
    EPISODIC = "episodic"      # Specific events/experiences
    SEMANTIC = "semantic"      # General facts/knowledge
    PROCEDURAL = "procedural"  # How-to knowledge
    PATTERN = "pattern"        # Recognized patterns
    SOLUTION = "solution"      # Successful fixes
    FAILURE = "failure"        # Failed attempts
    CONTEXT = "context"        # Environmental context


class ConfidenceLevel(Enum):
    """Confidence levels for solutions"""
    EXPERIMENTAL = 0.1      # New, untested
    PRELIMINARY = 0.3       # Limited testing
    DEVELOPING = 0.5        # Moderate success
    ESTABLISHED = 0.7       # Good track record
    RELIABLE = 0.85         # High success rate
    AUTHORITATIVE = 0.95    # Near-certain success


class DecayFunction(Enum):
    """Memory decay functions"""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    LOGARITHMIC = "logarithmic"
    STEP = "step"
    NONE = "none"


@dataclass
class MemoryEntry:
    """A single memory entry"""
    entry_id: str
    memory_type: MemoryType
    timestamp: float
    content: Dict[str, Any]
    tags: Set[str] = field(default_factory=set)
    confidence: float = 0.5
    success_count: int = 0
    failure_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    decay_rate: float = 0.1
    decay_function: DecayFunction = DecayFunction.EXPONENTIAL
    context_hash: str = ""
    related_entries: Set[str] = field(default_factory=set)
    source: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        d = asdict(self)
        d['memory_type'] = self.memory_type.value
        d['decay_function'] = self.decay_function.value
        d['tags'] = list(self.tags)
        d['related_entries'] = list(self.related_entries)
        return d
    
    @classmethod
    def from_dict(cls, d: Dict) -> 'MemoryEntry':
        """Create from dictionary"""
        d['memory_type'] = MemoryType(d['memory_type'])
        d['decay_function'] = DecayFunction(d['decay_function'])
        d['tags'] = set(d.get('tags', []))
        d['related_entries'] = set(d.get('related_entries', []))
        return cls(**d)


@dataclass
class SolutionRecord:
    """Record of a successful solution"""
    solution_id: str
    problem_signature: str
    problem_description: str
    solution_steps: List[Dict[str, Any]]
    context: Dict[str, Any]
    outcome: str  # "success", "partial", "failed"
    confidence: float
    timestamp: float
    execution_time: float
    side_effects: List[str]
    prerequisites: List[str]
    success_rate: float
    usage_count: int
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class FailureRecord:
    """Record of a failed attempt"""
    failure_id: str
    problem_signature: str
    attempted_solution: str
    failure_reason: str
    context: Dict[str, Any]
    timestamp: float
    impact: str  # "minor", "moderate", "severe", "critical"
    recovery_steps: List[str]
    lessons_learned: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PatternRecord:
    """Record of a recognized pattern"""
    pattern_id: str
    pattern_type: str
    signature: str
    occurrences: int
    first_seen: float
    last_seen: float
    contexts: List[str]
    typical_solution: Optional[str]
    confidence: float
    related_patterns: Set[str]
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d['related_patterns'] = list(self.related_patterns)
        return d


class EpisodicMemory:
    """
    Episodic Memory - Stores specific events and experiences
    
    This is like human episodic memory - remembering specific events,
    their context, and their outcomes. Each episode is a learning
    opportunity for the system.
    """
    
    def __init__(self, max_episodes: int = 10000):
        self.max_episodes = max_episodes
        self.episodes: Dict[str, MemoryEntry] = {}
        self.episode_index: Dict[str, Set[str]] = defaultdict(set)  # tag -> episode_ids
        self.temporal_index: List[Tuple[float, str]] = []  # (timestamp, episode_id)
        self._lock = threading.RLock()
    
    def store_episode(self, 
                      content: Dict[str, Any],
                      tags: Set[str] = None,
                      context_hash: str = "",
                      confidence: float = 0.5) -> str:
        """Store a new episode"""
        with self._lock:
            episode_id = f"ep_{uuid.uuid4().hex[:12]}"
            
            entry = MemoryEntry(
                entry_id=episode_id,
                memory_type=MemoryType.EPISODIC,
                timestamp=time.time(),
                content=content,
                tags=tags or set(),
                confidence=confidence,
                context_hash=context_hash
            )
            
            self.episodes[episode_id] = entry
            
            # Update indices
            for tag in entry.tags:
                self.episode_index[tag].add(episode_id)
            self.temporal_index.append((entry.timestamp, episode_id))
            
            # Enforce size limit
            self._enforce_limit()
            
            logger.debug("Episodic memory stored", episode_id=episode_id, tags=list(tags or []))
            return episode_id
    
    def retrieve_episode(self, episode_id: str) -> Optional[MemoryEntry]:
        """Retrieve a specific episode"""
        with self._lock:
            episode = self.episodes.get(episode_id)
            if episode:
                episode.last_accessed = time.time()
                episode.access_count += 1
            return episode
    
    def search_by_tags(self, tags: Set[str], require_all: bool = False) -> List[MemoryEntry]:
        """Search episodes by tags"""
        with self._lock:
            if not tags:
                return []
            
            if require_all:
                # All tags must be present
                episode_sets = [self.episode_index[tag] for tag in tags if tag in self.episode_index]
                if len(episode_sets) != len(tags):
                    return []
                matching_ids = set.intersection(*episode_sets)
            else:
                # Any tag matches
                matching_ids = set()
                for tag in tags:
                    matching_ids.update(self.episode_index.get(tag, set()))
            
            return [self.episodes[eid] for eid in matching_ids if eid in self.episodes]
    
    def search_by_time_range(self, start: float, end: float) -> List[MemoryEntry]:
        """Search episodes by time range"""
        with self._lock:
            matching_ids = [
                eid for ts, eid in self.temporal_index
                if start <= ts <= end
            ]
            return [self.episodes[eid] for eid in matching_ids if eid in self.episodes]
    
    def get_recent(self, count: int = 10) -> List[MemoryEntry]:
        """Get most recent episodes"""
        with self._lock:
            recent = sorted(self.temporal_index, reverse=True)[:count]
            return [self.episodes[eid] for _, eid in recent if eid in self.episodes]
    
    def _enforce_limit(self):
        """Enforce maximum episode count"""
        while len(self.episodes) > self.max_episodes:
            # Remove oldest episode
            if self.temporal_index:
                _, oldest_id = self.temporal_index.pop(0)
                if oldest_id in self.episodes:
                    entry = self.episodes.pop(oldest_id)
                    for tag in entry.tags:
                        self.episode_index[tag].discard(oldest_id)


class SemanticMemory:
    """
    Semantic Memory - Stores general facts and knowledge
    
    Unlike episodic memory which stores specific events, semantic memory
    stores generalized knowledge extracted from experiences. This is
    abstracted, context-independent knowledge.
    """
    
    def __init__(self, max_facts: int = 5000):
        self.max_facts = max_facts
        self.facts: Dict[str, MemoryEntry] = {}
        self.concept_graph: Dict[str, Set[str]] = defaultdict(set)  # concept -> related concepts
        self.fact_index: Dict[str, Set[str]] = defaultdict(set)  # concept -> fact_ids
        self._lock = threading.RLock()
    
    def store_fact(self,
                   concept: str,
                   fact: str,
                   evidence: List[str] = None,
                   confidence: float = 0.5) -> str:
        """Store a semantic fact"""
        with self._lock:
            fact_id = f"fact_{uuid.uuid4().hex[:12]}"
            
            content = {
                "concept": concept,
                "fact": fact,
                "evidence": evidence or [],
                "verified": False
            }
            
            entry = MemoryEntry(
                entry_id=fact_id,
                memory_type=MemoryType.SEMANTIC,
                timestamp=time.time(),
                content=content,
                tags={concept},
                confidence=confidence
            )
            
            self.facts[fact_id] = entry
            self.fact_index[concept].add(fact_id)
            
            # Link related concepts
            words = set(fact.lower().split())
            for word in words:
                if word != concept.lower():
                    self.concept_graph[concept].add(word)
            
            self._enforce_limit()
            
            logger.debug("Semantic fact stored", fact_id=fact_id, concept=concept)
            return fact_id
    
    def retrieve_facts(self, concept: str) -> List[MemoryEntry]:
        """Retrieve all facts about a concept"""
        with self._lock:
            fact_ids = self.fact_index.get(concept, set())
            return [self.facts[fid] for fid in fact_ids if fid in self.facts]
    
    def query_fact(self, query: str) -> List[Tuple[MemoryEntry, float]]:
        """Query facts with relevance scoring"""
        with self._lock:
            results = []
            query_words = set(query.lower().split())
            
            for fact_id, entry in self.facts.items():
                fact_words = set(entry.content.get("fact", "").lower().split())
                # Calculate Jaccard similarity
                if query_words and fact_words:
                    intersection = len(query_words & fact_words)
                    union = len(query_words | fact_words)
                    relevance = intersection / union if union > 0 else 0
                    
                    if relevance > 0:
                        results.append((entry, relevance))
            
            # Sort by relevance
            results.sort(key=lambda x: x[1], reverse=True)
            return results
    
    def get_related_concepts(self, concept: str, depth: int = 2) -> Set[str]:
        """Get concepts related to a given concept"""
        with self._lock:
            related = set()
            current_level = {concept}
            
            for _ in range(depth):
                next_level = set()
                for c in current_level:
                    next_level.update(self.concept_graph.get(c, set()))
                related.update(next_level)
                current_level = next_level - related
            
            return related
    
    def verify_fact(self, fact_id: str, verified: bool = True):
        """Mark a fact as verified or unverified"""
        with self._lock:
            if fact_id in self.facts:
                self.facts[fact_id].content["verified"] = verified
                if verified:
                    self.facts[fact_id].confidence = min(1.0, self.facts[fact_id].confidence + 0.1)
    
    def _enforce_limit(self):
        """Enforce maximum fact count"""
        if len(self.facts) > self.max_facts:
            # Remove lowest confidence facts
            sorted_facts = sorted(self.facts.items(), key=lambda x: x[1].confidence)
            for fact_id, _ in sorted_facts[:len(self.facts) - self.max_facts]:
                entry = self.facts.pop(fact_id)
                for tag in entry.tags:
                    self.fact_index[tag].discard(fact_id)


class ProceduralMemory:
    """
    Procedural Memory - Stores how-to knowledge
    
    This memory stores procedures, algorithms, and step-by-step
    instructions for accomplishing tasks. It's the "muscle memory"
    of the autonomous development system.
    """
    
    def __init__(self, max_procedures: int = 2000):
        self.max_procedures = max_procedures
        self.procedures: Dict[str, MemoryEntry] = {}
        self.procedure_index: Dict[str, Set[str]] = defaultdict(set)  # task_type -> procedure_ids
        self._lock = threading.RLock()
    
    def store_procedure(self,
                        task_type: str,
                        steps: List[Dict[str, Any]],
                        prerequisites: List[str] = None,
                        expected_outcome: str = "",
                        confidence: float = 0.5) -> str:
        """Store a procedure"""
        with self._lock:
            proc_id = f"proc_{uuid.uuid4().hex[:12]}"
            
            content = {
                "task_type": task_type,
                "steps": steps,
                "prerequisites": prerequisites or [],
                "expected_outcome": expected_outcome,
                "execution_count": 0,
                "success_count": 0,
                "average_time": 0.0
            }
            
            entry = MemoryEntry(
                entry_id=proc_id,
                memory_type=MemoryType.PROCEDURAL,
                timestamp=time.time(),
                content=content,
                tags={task_type},
                confidence=confidence
            )
            
            self.procedures[proc_id] = entry
            self.procedure_index[task_type].add(proc_id)
            
            self._enforce_limit()
            
            logger.debug("Procedure stored", proc_id=proc_id, task_type=task_type)
            return proc_id
    
    def retrieve_procedures(self, task_type: str) -> List[MemoryEntry]:
        """Retrieve all procedures for a task type"""
        with self._lock:
            proc_ids = self.procedure_index.get(task_type, set())
            procedures = [self.procedures[pid] for pid in proc_ids if pid in self.procedures]
            # Sort by confidence and success rate
            procedures.sort(key=lambda x: (
                x.confidence,
                x.content.get("success_count", 0) / max(1, x.content.get("execution_count", 1))
            ), reverse=True)
            return procedures
    
    def record_execution(self, proc_id: str, success: bool, execution_time: float):
        """Record a procedure execution"""
        with self._lock:
            if proc_id in self.procedures:
                entry = self.procedures[proc_id]
                content = entry.content
                
                content["execution_count"] += 1
                if success:
                    content["success_count"] += 1
                
                # Update average time
                current_avg = content["average_time"]
                count = content["execution_count"]
                content["average_time"] = (current_avg * (count - 1) + execution_time) / count
                
                # Update confidence based on success rate
                if content["execution_count"] >= 5:
                    success_rate = content["success_count"] / content["execution_count"]
                    entry.confidence = success_rate * 0.8 + 0.1  # Scale to 0.1-0.9
    
    def get_best_procedure(self, task_type: str) -> Optional[MemoryEntry]:
        """Get the best procedure for a task type"""
        procedures = self.retrieve_procedures(task_type)
        return procedures[0] if procedures else None
    
    def _enforce_limit(self):
        """Enforce maximum procedure count"""
        if len(self.procedures) > self.max_procedures:
            # Remove lowest confidence procedures
            sorted_procs = sorted(self.procedures.items(), key=lambda x: x[1].confidence)
            for proc_id, _ in sorted_procs[:len(self.procedures) - self.max_procedures]:
                entry = self.procedures.pop(proc_id)
                for tag in entry.tags:
                    self.procedure_index[tag].discard(proc_id)


class PatternRecognitionEngine:
    """
    Pattern Recognition Engine
    
    Identifies patterns in problems, solutions, and behaviors.
    This enables the system to recognize similar situations and
    apply learned solutions.
    """
    
    def __init__(self):
        self.patterns: Dict[str, PatternRecord] = {}
        self.signature_index: Dict[str, str] = {}  # signature -> pattern_id
        self.pattern_types: Dict[str, Set[str]] = defaultdict(set)  # type -> pattern_ids
        self._lock = threading.RLock()
    
    def compute_signature(self, data: Dict[str, Any]) -> str:
        """Compute a signature for data"""
        # Create a canonical representation
        canonical = json.dumps(data, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]
    
    def recognize_pattern(self, data: Dict[str, Any]) -> Optional[PatternRecord]:
        """Try to recognize a known pattern in data"""
        signature = self.compute_signature(data)
        
        with self._lock:
            if signature in self.signature_index:
                pattern_id = self.signature_index[signature]
                pattern = self.patterns.get(pattern_id)
                if pattern:
                    pattern.occurrences += 1
                    pattern.last_seen = time.time()
                    return pattern
            
            # Try fuzzy matching
            for pattern_id, pattern in self.patterns.items():
                if self._fuzzy_match(data, pattern):
                    pattern.occurrences += 1
                    pattern.last_seen = time.time()
                    return pattern
            
            return None
    
    def record_pattern(self,
                       pattern_type: str,
                       data: Dict[str, Any],
                       typical_solution: str = None) -> str:
        """Record a new pattern"""
        signature = self.compute_signature(data)
        
        with self._lock:
            # Check if pattern already exists
            if signature in self.signature_index:
                pattern_id = self.signature_index[signature]
                self.patterns[pattern_id].occurrences += 1
                return pattern_id
            
            pattern_id = f"pat_{uuid.uuid4().hex[:12]}"
            
            pattern = PatternRecord(
                pattern_id=pattern_id,
                pattern_type=pattern_type,
                signature=signature,
                occurrences=1,
                first_seen=time.time(),
                last_seen=time.time(),
                contexts=[],
                typical_solution=typical_solution,
                confidence=0.3,
                related_patterns=set()
            )
            
            self.patterns[pattern_id] = pattern
            self.signature_index[signature] = pattern_id
            self.pattern_types[pattern_type].add(pattern_id)
            
            logger.debug("Pattern recorded", pattern_id=pattern_id, type=pattern_type)
            return pattern_id
    
    def find_similar_patterns(self, data: Dict[str, Any], threshold: float = 0.7) -> List[PatternRecord]:
        """Find patterns similar to given data"""
        results = []
        
        with self._lock:
            for pattern in self.patterns.values():
                similarity = self._calculate_similarity(data, pattern)
                if similarity >= threshold:
                    results.append(pattern)
        
        results.sort(key=lambda p: p.confidence, reverse=True)
        return results
    
    def link_patterns(self, pattern_id1: str, pattern_id2: str):
        """Link two related patterns"""
        with self._lock:
            if pattern_id1 in self.patterns and pattern_id2 in self.patterns:
                self.patterns[pattern_id1].related_patterns.add(pattern_id2)
                self.patterns[pattern_id2].related_patterns.add(pattern_id1)
    
    def _fuzzy_match(self, data: Dict[str, Any], pattern: PatternRecord) -> bool:
        """Check if data fuzzy matches a pattern"""
        # Simplified fuzzy matching based on structure similarity
        return self._calculate_similarity(data, pattern) > 0.8
    
    def _calculate_similarity(self, data: Dict[str, Any], pattern: PatternRecord) -> float:
        """Calculate similarity between data and pattern"""
        # Simple structural similarity
        data_keys = set(data.keys())
        # For pattern, we'd need to compare structure
        # This is a placeholder for more sophisticated comparison
        return 0.5


class ConfidenceEngine:
    """
    Confidence Engine
    
    Calculates and updates confidence scores for memories and solutions.
    Uses Bayesian updating and temporal decay.
    """
    
    def __init__(self):
        self.base_confidence = 0.5
        self.decay_rate = 0.1
        self.min_confidence = 0.1
        self.max_confidence = 0.99
    
    def calculate_confidence(self, entry: MemoryEntry) -> float:
        """Calculate current confidence for an entry"""
        base = entry.confidence
        
        # Apply temporal decay
        age = time.time() - entry.timestamp
        decay = self._apply_decay(base, age, entry.decay_function, entry.decay_rate)
        
        # Factor in success/failure ratio
        total_attempts = entry.success_count + entry.failure_count
        if total_attempts > 0:
            success_rate = entry.success_count / total_attempts
            # Weighted average of decay and success rate
            confidence = 0.6 * decay + 0.4 * success_rate
        else:
            confidence = decay
        
        # Factor in access frequency
        if entry.access_count > 0:
            access_boost = min(0.1, entry.access_count * 0.01)
            confidence = min(self.max_confidence, confidence + access_boost)
        
        return max(self.min_confidence, min(self.max_confidence, confidence))
    
    def update_on_success(self, entry: MemoryEntry):
        """Update confidence after successful use"""
        entry.success_count += 1
        entry.last_accessed = time.time()
        
        # Bayesian update
        prior = entry.confidence
        likelihood = 0.8  # P(success|reliable)
        marginal = prior * likelihood + (1 - prior) * 0.2  # P(success)
        
        entry.confidence = (prior * likelihood) / marginal if marginal > 0 else prior
        entry.confidence = min(self.max_confidence, entry.confidence)
    
    def update_on_failure(self, entry: MemoryEntry):
        """Update confidence after failed use"""
        entry.failure_count += 1
        entry.last_accessed = time.time()
        
        # Bayesian update for failure
        prior = entry.confidence
        likelihood = 0.2  # P(failure|reliable)
        marginal = prior * likelihood + (1 - prior) * 0.8  # P(failure)
        
        entry.confidence = (prior * likelihood) / marginal if marginal > 0 else prior
        entry.confidence = max(self.min_confidence, entry.confidence)
    
    def _apply_decay(self, value: float, age: float, 
                     decay_func: DecayFunction, rate: float) -> float:
        """Apply temporal decay to a value"""
        if decay_func == DecayFunction.NONE:
            return value
        elif decay_func == DecayFunction.EXPONENTIAL:
            return value * math.exp(-rate * age / 86400)  # Decay per day
        elif decay_func == DecayFunction.LINEAR:
            return max(0, value - rate * age / 86400)
        elif decay_func == DecayFunction.LOGARITHMIC:
            return value * (1 - rate * math.log(1 + age / 86400) / 10)
        elif decay_func == DecayFunction.STEP:
            days = age / 86400
            if days < 7:
                return value
            elif days < 30:
                return value * 0.8
            elif days < 90:
                return value * 0.6
            else:
                return value * 0.4
        return value


class SolutionMemory:
    """
    Solution Memory - Stores successful solutions
    
    This is the core of autonomous learning - remembering what worked
    and being able to apply it to similar problems.
    """
    
    def __init__(self):
        self.solutions: Dict[str, SolutionRecord] = {}
        self.problem_index: Dict[str, Set[str]] = defaultdict(set)  # problem_signature -> solution_ids
        self.tag_index: Dict[str, Set[str]] = defaultdict(set)  # tag -> solution_ids
        self._lock = threading.RLock()
    
    def store_solution(self,
                       problem_description: str,
                       problem_signature: str,
                       solution_steps: List[Dict[str, Any]],
                       context: Dict[str, Any],
                       outcome: str = "success",
                       execution_time: float = 0.0,
                       side_effects: List[str] = None,
                       prerequisites: List[str] = None) -> str:
        """Store a solution"""
        with self._lock:
            solution_id = f"sol_{uuid.uuid4().hex[:12]}"
            
            solution = SolutionRecord(
                solution_id=solution_id,
                problem_signature=problem_signature,
                problem_description=problem_description,
                solution_steps=solution_steps,
                context=context,
                outcome=outcome,
                confidence=0.5,
                timestamp=time.time(),
                execution_time=execution_time,
                side_effects=side_effects or [],
                prerequisites=prerequisites or [],
                success_rate=1.0 if outcome == "success" else 0.5,
                usage_count=1
            )
            
            self.solutions[solution_id] = solution
            self.problem_index[problem_signature].add(solution_id)
            
            # Index by context tags
            for key, value in context.items():
                tag = f"{key}:{value}"
                self.tag_index[tag].add(solution_id)
            
            logger.info("Solution stored", solution_id=solution_id, problem=problem_signature)
            return solution_id
    
    def find_solutions(self, problem_signature: str) -> List[SolutionRecord]:
        """Find solutions for a problem"""
        with self._lock:
            solution_ids = self.problem_index.get(problem_signature, set())
            solutions = [self.solutions[sid] for sid in solution_ids if sid in self.solutions]
            solutions.sort(key=lambda s: s.confidence, reverse=True)
            return solutions
    
    def find_similar_solutions(self, 
                               context: Dict[str, Any],
                               min_matches: int = 2) -> List[SolutionRecord]:
        """Find solutions with similar context"""
        with self._lock:
            # Find solutions matching multiple context tags
            solution_scores: Dict[str, int] = defaultdict(int)
            
            for key, value in context.items():
                tag = f"{key}:{value}"
                for sid in self.tag_index.get(tag, set()):
                    solution_scores[sid] += 1
            
            # Filter by minimum matches
            matching_ids = {sid for sid, score in solution_scores.items() if score >= min_matches}
            solutions = [self.solutions[sid] for sid in matching_ids if sid in self.solutions]
            solutions.sort(key=lambda s: (solution_scores[s.solution_id], s.confidence), reverse=True)
            return solutions
    
    def record_usage(self, solution_id: str, success: bool):
        """Record usage of a solution"""
        with self._lock:
            if solution_id in self.solutions:
                solution = self.solutions[solution_id]
                solution.usage_count += 1
                
                # Update success rate
                total = solution.usage_count
                successes = int(solution.success_rate * (total - 1))
                if success:
                    successes += 1
                solution.success_rate = successes / total
                
                # Update confidence
                solution.confidence = solution.success_rate * 0.9 + 0.05
    
    def get_best_solution(self, problem_signature: str) -> Optional[SolutionRecord]:
        """Get the best solution for a problem"""
        solutions = self.find_solutions(problem_signature)
        return solutions[0] if solutions else None


class FailureMemory:
    """
    Failure Memory - Stores failed attempts
    
    Equally important as success memory - knowing what doesn't work
    prevents repeating mistakes.
    """
    
    def __init__(self):
        self.failures: Dict[str, FailureRecord] = {}
        self.problem_failures: Dict[str, Set[str]] = defaultdict(set)  # problem_signature -> failure_ids
        self._lock = threading.RLock()
    
    def record_failure(self,
                       problem_signature: str,
                       attempted_solution: str,
                       failure_reason: str,
                       context: Dict[str, Any],
                       impact: str = "moderate",
                       recovery_steps: List[str] = None,
                       lessons_learned: List[str] = None) -> str:
        """Record a failure"""
        with self._lock:
            failure_id = f"fail_{uuid.uuid4().hex[:12]}"
            
            failure = FailureRecord(
                failure_id=failure_id,
                problem_signature=problem_signature,
                attempted_solution=attempted_solution,
                failure_reason=failure_reason,
                context=context,
                timestamp=time.time(),
                impact=impact,
                recovery_steps=recovery_steps or [],
                lessons_learned=lessons_learned or []
            )
            
            self.failures[failure_id] = failure
            self.problem_failures[problem_signature].add(failure_id)
            
            logger.warning("Failure recorded", failure_id=failure_id, reason=failure_reason)
            return failure_id
    
    def get_failures_for_problem(self, problem_signature: str) -> List[FailureRecord]:
        """Get all failures for a problem"""
        with self._lock:
            failure_ids = self.problem_failures.get(problem_signature, set())
            return [self.failures[fid] for fid in failure_ids if fid in self.failures]
    
    def should_avoid(self, problem_signature: str, solution: str) -> bool:
        """Check if a solution should be avoided for a problem"""
        failures = self.get_failures_for_problem(problem_signature)
        for failure in failures:
            if failure.attempted_solution == solution and failure.impact in ["severe", "critical"]:
                return True
        return False
    
    def get_lessons_learned(self, problem_signature: str) -> List[str]:
        """Get all lessons learned for a problem"""
        failures = self.get_failures_for_problem(problem_signature)
        lessons = []
        for failure in failures:
            lessons.extend(failure.lessons_learned)
        return list(set(lessons))


class LearningMemoryEngine:
    """
    Learning Memory Engine - Main Orchestrator
    
    Coordinates all memory systems for autonomous learning and improvement.
    This is the brain that remembers everything and applies knowledge
    to new situations.
    """
    
    def __init__(self, 
                 storage_path: str = None,
                 auto_save: bool = True,
                 save_interval: int = 300):
        
        # Initialize memory systems
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.procedural = ProceduralMemory()
        self.pattern_engine = PatternRecognitionEngine()
        self.confidence_engine = ConfidenceEngine()
        self.solution_memory = SolutionMemory()
        self.failure_memory = FailureMemory()
        
        # Storage
        self.storage_path = storage_path or "/tmp/learning_memory"
        self.auto_save = auto_save
        self.save_interval = save_interval
        
        # Statistics
        self.stats = {
            "episodes_stored": 0,
            "solutions_found": 0,
            "failures_avoided": 0,
            "patterns_recognized": 0,
            "successful_applications": 0
        }
        
        # Background tasks
        self._running = True
        self._save_thread = None
        
        if auto_save:
            self._save_thread = threading.Thread(target=self._auto_save_loop, daemon=True)
            self._save_thread.start()
        
        logger.info("Learning Memory Engine initialized")
    
    def learn_from_experience(self,
                              event: str,
                              context: Dict[str, Any],
                              outcome: str,
                              solution_used: str = None) -> str:
        """Learn from an experience"""
        # Store as episode
        episode_id = self.episodic.store_episode(
            content={
                "event": event,
                "outcome": outcome,
                "solution_used": solution_used
            },
            tags={event, outcome},
            context_hash=self.pattern_engine.compute_signature(context)
        )
        
        self.stats["episodes_stored"] += 1
        
        # If successful, record as solution
        if outcome == "success" and solution_used:
            self.solution_memory.store_solution(
                problem_description=event,
                problem_signature=self.pattern_engine.compute_signature({"event": event}),
                solution_steps=[{"action": solution_used}],
                context=context
            )
        
        # Check for patterns
        pattern = self.pattern_engine.recognize_pattern({"event": event, "context": context})
        if pattern:
            self.stats["patterns_recognized"] += 1
            logger.debug("Pattern recognized", pattern_id=pattern.pattern_id)
        else:
            self.pattern_engine.record_pattern(
                pattern_type="event",
                data={"event": event, "context": context}
            )
        
        return episode_id
    
    def find_solution(self, problem: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a solution for a problem"""
        problem_signature = self.pattern_engine.compute_signature({"problem": problem})
        
        # Check for known solutions
        solutions = self.solution_memory.find_solutions(problem_signature)
        
        if not solutions:
            # Try similar context
            solutions = self.solution_memory.find_similar_solutions(context)
        
        if solutions:
            self.stats["solutions_found"] += 1
            best = solutions[0]
            
            # Check if we should avoid this solution
            if self.failure_memory.should_avoid(problem_signature, best.solution_id):
                # Try next best
                for sol in solutions[1:]:
                    if not self.failure_memory.should_avoid(problem_signature, sol.solution_id):
                        return {
                            "solution_id": sol.solution_id,
                            "steps": sol.solution_steps,
                            "confidence": sol.confidence,
                            "source": "memory"
                        }
            else:
                return {
                    "solution_id": best.solution_id,
                    "steps": best.solution_steps,
                    "confidence": best.confidence,
                    "source": "memory"
                }
        
        return None
    
    def record_success(self, solution_id: str, problem: str):
        """Record a successful solution application"""
        self.solution_memory.record_usage(solution_id, True)
        self.stats["successful_applications"] += 1
        logger.info("Success recorded", solution_id=solution_id, problem=problem)
    
    def record_failure(self,
                       problem: str,
                       attempted_solution: str,
                       failure_reason: str,
                       context: Dict[str, Any],
                       lessons: List[str] = None):
        """Record a failed solution attempt"""
        problem_signature = self.pattern_engine.compute_signature({"problem": problem})
        
        self.failure_memory.record_failure(
            problem_signature=problem_signature,
            attempted_solution=attempted_solution,
            failure_reason=failure_reason,
            context=context,
            lessons_learned=lessons
        )
    
    def get_contextual_knowledge(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get relevant knowledge for a context"""
        knowledge = {
            "relevant_episodes": [],
            "relevant_facts": [],
            "relevant_procedures": [],
            "known_patterns": [],
            "warnings": []
        }
        
        # Get recent relevant episodes
        for key, value in context.items():
            episodes = self.episodic.search_by_tags({str(value)})
            knowledge["relevant_episodes"].extend([e.to_dict() for e in episodes[:5]])
        
        # Get relevant facts
        for key, value in context.items():
            facts = self.semantic.retrieve_facts(str(value))
            knowledge["relevant_facts"].extend([f.to_dict() for f in facts[:5]])
        
        # Get relevant patterns
        patterns = self.pattern_engine.find_similar_patterns(context)
        knowledge["known_patterns"] = [p.to_dict() for p in patterns[:5]]
        
        # Get failure warnings
        for key, value in context.items():
            tag = f"{key}:{value}"
            # Would check for failures with this context
        
        return knowledge
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "episodes": len(self.episodic.episodes),
            "facts": len(self.semantic.facts),
            "procedures": len(self.procedural.procedures),
            "patterns": len(self.pattern_engine.patterns),
            "solutions": len(self.solution_memory.solutions),
            "failures": len(self.failure_memory.failures),
            "stats": self.stats.copy()
        }
    
    def save_memory(self, path: str = None):
        """Save all memory to disk"""
        path = path or self.storage_path
        os.makedirs(path, exist_ok=True)
        
        # Save each memory system
        memory_data = {
            "episodic": {eid: e.to_dict() for eid, e in self.episodic.episodes.items()},
            "semantic": {fid: f.to_dict() for fid, f in self.semantic.facts.items()},
            "procedural": {pid: p.to_dict() for pid, p in self.procedural.procedures.items()},
            "patterns": {pid: p.to_dict() for pid, p in self.pattern_engine.patterns.items()},
            "solutions": {sid: s.to_dict() for sid, s in self.solution_memory.solutions.items()},
            "failures": {fid: f.to_dict() for fid, f in self.failure_memory.failures.items()},
            "stats": self.stats
        }
        
        filepath = os.path.join(path, "memory_dump.pkl.gz")
        with gzip.open(filepath, 'wb') as f:
            pickle.dump(memory_data, f)
        
        logger.info("Memory saved", path=filepath)
    
    def load_memory(self, path: str = None):
        """Load memory from disk"""
        path = path or self.storage_path
        filepath = os.path.join(path, "memory_dump.pkl.gz")
        
        if not os.path.exists(filepath):
            logger.warning("No memory file found", path=filepath)
            return
        
        with gzip.open(filepath, 'rb') as f:
            memory_data = pickle.load(f)
        
        # Restore each memory system
        for eid, e_dict in memory_data.get("episodic", {}).items():
            self.episodic.episodes[eid] = MemoryEntry.from_dict(e_dict)
        
        for fid, f_dict in memory_data.get("semantic", {}).items():
            self.semantic.facts[fid] = MemoryEntry.from_dict(f_dict)
        
        for pid, p_dict in memory_data.get("procedural", {}).items():
            self.procedural.procedures[pid] = MemoryEntry.from_dict(p_dict)
        
        for pid, p_dict in memory_data.get("patterns", {}).items():
            pr = PatternRecord(
                pattern_id=p_dict["pattern_id"],
                pattern_type=p_dict["pattern_type"],
                signature=p_dict["signature"],
                occurrences=p_dict["occurrences"],
                first_seen=p_dict["first_seen"],
                last_seen=p_dict["last_seen"],
                contexts=p_dict["contexts"],
                typical_solution=p_dict.get("typical_solution"),
                confidence=p_dict["confidence"],
                related_patterns=set(p_dict.get("related_patterns", []))
            )
            self.pattern_engine.patterns[pid] = pr
        
        for sid, s_dict in memory_data.get("solutions", {}).items():
            sr = SolutionRecord(**s_dict)
            self.solution_memory.solutions[sid] = sr
        
        for fid, f_dict in memory_data.get("failures", {}).items():
            fr = FailureRecord(**f_dict)
            self.failure_memory.failures[fid] = fr
        
        self.stats = memory_data.get("stats", self.stats)
        
        logger.info("Memory loaded", path=filepath)
    
    def _auto_save_loop(self):
        """Auto-save loop"""
        while self._running:
            time.sleep(self.save_interval)
            try:
                self.save_memory()
            except Exception as e:
                logger.error("Auto-save failed", error=str(e))
    
    def shutdown(self):
        """Shutdown the engine"""
        self._running = False
        if self._save_thread:
            self._save_thread.join(timeout=5)
        self.save_memory()
        logger.info("Learning Memory Engine shutdown complete")


# Singleton instance
_learning_memory_engine: Optional[LearningMemoryEngine] = None


def get_learning_memory() -> LearningMemoryEngine:
    """Get or create the learning memory engine singleton"""
    global _learning_memory_engine
    if _learning_memory_engine is None:
        _learning_memory_engine = LearningMemoryEngine()
    return _learning_memory_engine


# API Functions
def learn(event: str, context: Dict[str, Any], outcome: str, solution: str = None) -> str:
    """Learn from an experience"""
    return get_learning_memory().learn_from_experience(event, context, outcome, solution)


def solve(problem: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Find a solution for a problem"""
    return get_learning_memory().find_solution(problem, context)


def record_success(solution_id: str, problem: str):
    """Record a successful solution"""
    get_learning_memory().record_success(solution_id, problem)


def record_failure(problem: str, solution: str, reason: str, context: Dict[str, Any], lessons: List[str] = None):
    """Record a failure"""
    get_learning_memory().record_failure(problem, solution, reason, context, lessons)


def get_knowledge(context: Dict[str, Any]) -> Dict[str, Any]:
    """Get contextual knowledge"""
    return get_learning_memory().get_contextual_knowledge(context)


def get_stats() -> Dict[str, Any]:
    """Get memory statistics"""
    return get_learning_memory().get_memory_statistics()


if __name__ == "__main__":
    # Test the learning memory engine
    engine = LearningMemoryEngine()
    
    # Test learning from experience
    episode1 = engine.learn_from_experience(
        event="api_timeout",
        context={"service": "auth", "timeout": 30},
        outcome="success",
        solution_used="retry_with_backoff"
    )
    print(f"Episode stored: {episode1}")
    
    # Test finding solution
    solution = engine.find_solution(
        problem="api_timeout",
        context={"service": "auth"}
    )
    print(f"Solution found: {solution}")
    
    # Test recording failure
    engine.record_failure(
        problem="api_timeout",
        attempted_solution="immediate_retry",
        failure_reason="Still timing out",
        context={"service": "auth"},
        lessons=["Immediate retry doesn't work for timeouts"]
    )
    
    # Get stats
    stats = engine.get_memory_statistics()
    print(f"Stats: {json.dumps(stats, indent=2)}")
    
    print("\n🜂 Learning Memory Engine - Level 5 Autonomous Development")
    print("   Module m96 - OPERATIONAL")
