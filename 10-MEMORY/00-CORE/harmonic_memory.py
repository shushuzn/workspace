"""
Harmonic Memory Store: MEMORA Implementation
Based on arXiv:2602.03315

Dual-layer memory representation that balances abstraction and specificity:
- Primary Abstractions: Index concrete values, consolidate updates
- Cue Anchors: Expand retrieval access, connect related memories

Key benefit: 98% token reduction through abstraction
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any
from datetime import datetime
from enum import Enum
import hashlib
import json


class AbstractionLevel(Enum):
    HIGH = "high"  # 高度抽象
    MEDIUM = "medium"  # 中等抽象
    LOW = "low"  # 低抽象，保留细节


@dataclass
class MemoryValue:
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "metadata": self.metadata,
        }


@dataclass
class HarmonicMemoryEntry:
    memory_id: str
    primary_abstraction: str
    concrete_values: List[MemoryValue]
    cue_anchors: List[str]
    connections: Set[str] = field(default_factory=set)
    abstraction_level: AbstractionLevel = AbstractionLevel.MEDIUM
    entities: List[str] = field(default_factory=list)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    importance_score: float = 0.5

    def to_dict(self) -> Dict:
        return {
            "memory_id": self.memory_id,
            "primary_abstraction": self.primary_abstraction,
            "concrete_values": [v.to_dict() for v in self.concrete_values],
            "cue_anchors": self.cue_anchors,
            "connections": list(self.connections),
            "abstraction_level": self.abstraction_level.value,
            "entities": self.entities,
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "importance_score": self.importance_score,
        }


class HarmonicMemoryStore:
    """
    Dual-layer memory store with harmonic retrieval.

    Layers:
    1. Abstraction Layer: Primary abstractions index concrete values
    2. Concrete Layer: Raw memory values with metadata

    Retrieval uses harmonic mean of semantic similarity and cue matching
    to balance between abstract and specific results.
    """

    def __init__(
        self,
        abstraction_model: Optional[Any] = None,
        embedding_model: Optional[Any] = None,
        max_abstractions: int = 1000,
        cue_match_boost: float = 1.5,
    ):
        self.abstractions: Dict[str, HarmonicMemoryEntry] = {}
        self.concrete_values: Dict[str, MemoryValue] = {}
        self.cue_index: Dict[str, Set[str]] = {}
        self.connection_graph: Dict[str, Set[str]] = {}

        self.abstraction_model = abstraction_model
        self.embedding_model = embedding_model
        self.max_abstractions = max_abstractions
        self.cue_match_boost = cue_match_boost

        self._embedding_cache: Dict[str, List[float]] = {}

    def add(
        self,
        memory: str,
        cue_anchors: Optional[List[str]] = None,
        entities: Optional[List[str]] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> str:
        memory_id = self._generate_memory_id(memory)

        if memory_id in self.abstractions:
            self._update_existing(memory_id, memory, source, metadata)
            return memory_id

        abstraction = self._create_abstraction(memory, entities)

        concrete = MemoryValue(
            content=memory,
            timestamp=datetime.now(),
            source=source,
            metadata=metadata or {},
        )

        entry = HarmonicMemoryEntry(
            memory_id=memory_id,
            primary_abstraction=abstraction["summary"],
            concrete_values=[concrete],
            cue_anchors=cue_anchors or abstraction["cue_anchors"],
            entities=abstraction["entities"],
            abstraction_level=abstraction["level"],
            connections=set(),
        )

        self.abstractions[memory_id] = entry
        self.concrete_values[memory_id] = concrete

        for cue in entry.cue_anchors:
            if cue not in self.cue_index:
                self.cue_index[cue] = set()
            self.cue_index[cue].add(memory_id)

        self.connection_graph[memory_id] = set()

        self._auto_connect(memory_id)

        return memory_id

    def retrieve(
        self,
        query: str,
        mode: str = "harmonic",
        limit: int = 10,
        expand_connections: bool = True,
    ) -> List[HarmonicMemoryEntry]:
        if mode == "detailed":
            return self._retrieve_detailed(query, limit)
        if mode == "harmonic":
            return self._retrieve_harmonic(query, limit, expand_connections)
        elif mode == "semantic":
            return self._retrieve_semantic(query, limit)
        elif mode == "cue":
            return self._retrieve_cue(query, limit)
        else:
            return self._retrieve_harmonic(query, limit, expand_connections)

    def get(self, memory_id: str) -> Optional[HarmonicMemoryEntry]:
        entry = self.abstractions.get(memory_id)
        if entry:
            entry.last_accessed = datetime.now()
            entry.access_count += 1
        return entry

    def get_concrete(self, memory_id: str) -> Optional[MemoryValue]:
        return self.concrete_values.get(memory_id)

    def _create_abstraction(
        self, memory: str, entities: Optional[List[str]] = None
    ) -> Dict:
        if self.abstraction_model:
            return self._llm_abstraction(memory, entities)

        return self._rule_based_abstraction(memory, entities)

    def _llm_abstraction(self, memory: str, entities: Optional[List[str]]) -> Dict:
        if not self.abstraction_model:
            return self._rule_based_abstraction(memory, entities)

        summary_prompt = f"Summarize this memory in 1-2 sentences:\n{memory}"
        summary = self.abstraction_model.predict(summary_prompt)

        cue_prompt = (
            f"Extract 3-5 key search terms (cue anchors) for this memory:\n{memory}"
        )
        cues = self.abstraction_model.predict(cue_prompt).split(", ")

        level_prompt = f"Rate abstraction level (high/medium/low) for: {memory}"
        level_str = self.abstraction_model.predict(level_prompt).lower()

        level = AbstractionLevel.MEDIUM
        if "high" in level_str:
            level = AbstractionLevel.HIGH
        elif "low" in level_str:
            level = AbstractionLevel.LOW

        return {
            "summary": summary,
            "cue_anchors": [c.strip() for c in cues],
            "entities": entities or [],
            "level": level,
        }

    def _rule_based_abstraction(
        self, memory: str, entities: Optional[List[str]]
    ) -> Dict:
        words = memory.lower().split()

        important_keywords = {
            "high": [
                "important",
                "critical",
                "key",
                "essential",
                "核心",
                "关键",
                "重要",
            ],
            "medium": ["learned", "found", "discovered", "发现", "学习", "经验"],
            "low": ["detail", "specific", "具体", "细节"],
        }

        level = AbstractionLevel.MEDIUM
        for word in words:
            if any(kw in word for kw in important_keywords["high"]):
                level = AbstractionLevel.HIGH
                break
            elif any(kw in word for kw in important_keywords["low"]):
                level = AbstractionLevel.LOW

        summary = memory[:100] + "..." if len(memory) > 100 else memory

        cue_anchors = []
        if entities:
            cue_anchors.extend(entities[:5])

        keywords = [w for w in words if len(w) > 4][:5]
        cue_anchors.extend(keywords)

        return {
            "summary": summary,
            "cue_anchors": list(set(cue_anchors)),
            "entities": entities or [],
            "level": level,
        }

    def _update_existing(
        self,
        memory_id: str,
        memory: str,
        source: Optional[str],
        metadata: Optional[Dict],
    ):
        entry = self.abstractions[memory_id]

        concrete = MemoryValue(
            content=memory,
            timestamp=datetime.now(),
            source=source,
            metadata=metadata or {},
        )
        entry.concrete_values.append(concrete)
        self.concrete_values[memory_id] = concrete

        entry.access_count += 1
        entry.last_accessed = datetime.now()

    def _retrieve_harmonic(
        self, query: str, limit: int, expand: bool
    ) -> List[HarmonicMemoryEntry]:
        semantic_scores = self._semantic_search(query)
        cue_scores = self._cue_search(query)

        combined = {}
        all_ids = set(semantic_scores) | set(cue_scores)

        for memory_id in all_ids:
            s = semantic_scores.get(memory_id, 0.0)
            c = cue_scores.get(memory_id, 0.0)
            combined[memory_id] = self._harmonic_mean(s, c)

        if expand:
            expanded = set()
            for mid in list(combined.keys())[:5]:
                expanded.update(self._expand_via_connections(mid, depth=1))
            for mid in expanded:
                if mid not in combined:
                    combined[mid] = 0.3

        sorted_ids = sorted(combined.items(), key=lambda x: x[1], reverse=True)

        results = []
        for mid, score in sorted_ids[:limit]:
            entry = self.abstractions.get(mid)
            if entry:
                results.append(entry)

        return results

    def _semantic_search(self, query: str) -> Dict[str, float]:
        query_embedding = self._get_embedding(query)

        scores = {}
        for memory_id, entry in self.abstractions.items():
            abstraction_embedding = self._get_embedding(entry.primary_abstraction)
            score = self._cosine_similarity(query_embedding, abstraction_embedding)
            scores[memory_id] = score

        return scores

    def _cue_search(self, query: str) -> Dict[str, float]:
        query_lower = query.lower()
        query_words = set(query_lower.split())

        scores = {}
        for cue, memory_ids in self.cue_index.items():
            cue_words = set(cue.lower().split())
            overlap = len(query_words & cue_words)
            if overlap > 0:
                for mid in memory_ids:
                    boost = self.cue_match_boost if overlap >= 2 else 1.0
                    scores[mid] = scores.get(mid, 0.0) + (overlap * 0.2 * boost)

        max_score = max(scores.values()) if scores else 1.0
        if max_score > 0:
            scores = {k: v / max_score for k, v in scores.items()}

        return scores

    def _retrieve_semantic(self, query: str, limit: int) -> List[HarmonicMemoryEntry]:
        scores = self._semantic_search(query)
        sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [
            self.abstractions[mid]
            for mid, _ in sorted_ids[:limit]
            if mid in self.abstractions
        ]

    def _retrieve_cue(self, query: str, limit: int) -> List[HarmonicMemoryEntry]:
        scores = self._cue_search(query)
        sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [
            self.abstractions[mid]
            for mid, _ in sorted_ids[:limit]
            if mid in self.abstractions
        ]

    def _retrieve_detailed(self, query: str, limit: int) -> List[HarmonicMemoryEntry]:
        entries = self._retrieve_harmonic(query, limit, expand=True)
        return entries[:limit]

    def _expand_via_connections(self, memory_id: str, depth: int = 2) -> Set[str]:
        expanded = {memory_id}
        current = {memory_id}

        for _ in range(depth):
            next_layer = set()
            for mid in current:
                connections = self.connection_graph.get(mid, set())
                next_layer.update(connections)
            expanded.update(next_layer)
            current = next_layer

        return expanded

    def _auto_connect(self, memory_id: str):
        entry = self.abstractions[memory_id]

        for other_id, other_entry in self.abstractions.items():
            if other_id == memory_id:
                continue

            connection_score = self._calculate_connection(entry, other_entry)

            if connection_score > 0.3:
                self.connection_graph[memory_id].add(other_id)
                self.connection_graph[other_id].add(memory_id)

    def _calculate_connection(
        self, entry1: HarmonicMemoryEntry, entry2: HarmonicMemoryEntry
    ) -> float:
        entity_overlap = len(set(entry1.entities) & set(entry2.entities))
        if entity_overlap > 0:
            return min(1.0, entity_overlap * 0.3)

        cue_overlap = len(set(entry1.cue_anchors) & set(entry2.cue_anchors))
        if cue_overlap > 0:
            return min(0.8, cue_overlap * 0.2)

        return 0.0

    def _get_embedding(self, text: str) -> List[float]:
        if text in self._embedding_cache:
            return self._embedding_cache[text]

        if self.embedding_model:
            embedding = self.embedding_model.embed(text)
        else:
            embedding = self._simple_embedding(text)

        self._embedding_cache[text] = embedding
        return embedding

    def _simple_embedding(self, text: str) -> List[float]:
        import hashlib

        hash_digest = hashlib.md5(text.encode()).digest()
        values = [b / 255.0 for b in hash_digest[:16]]
        while len(values) < 16:
            values.append(0.0)

        norm = sum(v * v for v in values) ** 0.5
        if norm > 0:
            values = [v / norm for v in values]

        return values

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        if len(a) != len(b):
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def _harmonic_mean(self, x: float, y: float) -> float:
        if x == 0 and y == 0:
            return 0.0
        return 2 * x * y / (x + y + 1e-10)

    def _generate_memory_id(self, memory: str) -> str:
        return hashlib.md5(memory.encode()[:50]).hexdigest()[:12]

    def stats(self) -> Dict:
        return {
            "total_entries": len(self.abstractions),
            "total_concrete": len(self.concrete_values),
            "cue_count": len(self.cue_index),
            "connection_count": sum(len(c) for c in self.connection_graph.values()),
            "avg_access_count": sum(e.access_count for e in self.abstractions.values())
            / max(1, len(self.abstractions)),
        }

    def to_dict(self) -> Dict:
        return {
            "abstractions": {k: v.to_dict() for k, v in self.abstractions.items()},
            "stats": self.stats(),
        }


def demo():
    print("=" * 60)
    print("MEMORA Harmonic Memory Store Demo")
    print("=" * 60)

    store = HarmonicMemoryStore()

    store.add(
        "Learned about FLARE planner - it solves myopic commitment in LLM agents",
        entities=["FLARE", "planner", "LLM"],
        source="research",
    )

    store.add(
        "MEMORA paper shows 98% token reduction through dual-layer memory",
        entities=["MEMORA", "memory", "token"],
        source="research",
    )

    store.add(
        "7-persona system in OpenClaw achieves 96/100 composite score",
        entities=["OpenClaw", "persona", "score"],
        source="memory",
    )

    print(f"\nAdded 3 memories")
    print(f"Stats: {store.stats()}")

    print("\n--- Query: 'planner agent' (harmonic mode) ---")
    results = store.retrieve("planner agent", mode="harmonic", limit=3)
    for r in results:
        print(f"\n{r.primary_abstraction}")
        print(f"  Cues: {r.cue_anchors}")
        print(f"  Entities: {r.entities}")


if __name__ == "__main__":
    demo()
