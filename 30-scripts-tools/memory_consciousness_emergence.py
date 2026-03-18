#!/usr/bin/env python3
"""
Memory Consciousness Emergence - From Passive Storage to Active Awareness
===========================================================================
Implements consciousness emergence analogy for memory - system develops
self-awareness, introspection, and creative insight through complex interactions.

Key Theories:
- Global Workspace Theory (GWT): Information becomes conscious when broadcast globally
- Integrated Information Theory (IIT): Consciousness = Φ (integrated information)
- Higher-Order Thought (HOT): Consciousness requires thinking about thinking
- Self-Reference: System can refer to itself recursively
- Reflexivity: System can observe and modify its own structure
- Emergent Properties: Whole is greater than sum of parts
- Hard Problem: Subjective experience (qualia) from physical processes
- Panpsychism: Consciousness as fundamental property

Usage:
    python memory_consciousness_emergence.py --global-workspace "MEMORY.md"
    python memory_consciousness_emergence.py --integrated-info "MEMORY.md"
    python memory_consciousness_emergence.py --higher-order-thought
    python memory_consciousness_emergence.py --self-reference
    python memory_consciousness_emergence.py --reflexivity
    python memory_consciousness_emergence.py --emergence
    python memory_consciousness_emergence.py --qualia
    python memory_consciousness_emergence.py --status
"""

import os
import sys
import json
import logging
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from collections import defaultdict, Counter, deque
from itertools import combinations
import hashlib

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

@dataclass
class ConsciousnessConfig:
    """Consciousness emergence configuration"""

    # Global Workspace
    GW_THRESHOLD: float = 0.7              # Threshold for global broadcast
    GW_CAPACITY: int = 7                   # Miller's number (7±2)
    ATTENTION_WEIGHT: float = 0.8          # Attention modulation

    # Integrated Information
    PHI_THRESHOLD: float = 0.5             # Minimum Φ for consciousness
    INTEGRATION_DEPTH: int = 3             # Depth of causal analysis

    # Higher-Order Thought
    HOT_DEPTH: int = 2                     # Levels of meta-cognition
    SELF_MODEL_COMPLEXITY: int = 5         # Complexity of self-model

    # Emergence
    EMERGENCE_THRESHOLD: float = 0.8       # Threshold for emergent property
    SYNERGY_WEIGHT: float = 0.6            # Weight of synergistic interactions

    # Paths
    WORKSPACE: str = os.path.join(os.path.dirname(__file__), '..')
    CONSCIOUSNESS_STATE: str = os.path.join(WORKSPACE, 'data', 'consciousness_state.json')
    CONSCIOUSNESS_CONFIG: str = os.path.join(WORKSPACE, 'data', 'consciousness_config.json')
    GLOBAL_WORKSPACE: str = os.path.join(WORKSPACE, 'data', 'global_workspace.json')

# ============================================================================
# Consciousness Structures
# ============================================================================

@dataclass
class CognitiveModule:
    """A specialized cognitive module"""
    module_id: str
    function: str               # What this module does
    activation: float           # Current activation level (0-1)
    connectivity: List[str]     # Connected modules
    information_content: float  # Bits of information
    causal_power: float         # Cause-effect power

    def to_dict(self) -> Dict:
        return {
            'module_id': self.module_id,
            'function': self.function,
            'activation': self.activation,
            'connectivity': self.connectivity,
            'information_content': self.information_content,
            'causal_power': self.causal_power
        }

@dataclass
class GlobalWorkspaceState:
    """State of the global workspace"""
    workspace_id: str
    active_contents: List[Dict]     # Currently conscious contents
    broadcast_history: List[Dict]   # History of broadcasts
    attention_focus: str = None     # Current focus of attention
    consciousness_level: float = 0.0  # Overall consciousness level
    created_at: datetime = field(default_factory=datetime.now)
    last_broadcast: datetime = None

    def to_dict(self) -> Dict:
        return {
            'workspace_id': self.workspace_id,
            'active_contents': self.active_contents,
            'broadcast_history': self.broadcast_history[-100:],  # Last 100
            'attention_focus': self.attention_focus,
            'consciousness_level': self.consciousness_level,
            'created_at': self.created_at.isoformat(),
            'last_broadcast': self.last_broadcast.isoformat() if self.last_broadcast else None
        }

@dataclass
class IntegratedInformation:
    """Integrated information (Φ) measurement"""
    phi_value: float              # Integrated information
    cause_info: float             # Cause information
    effect_info: float            # Effect information
    min_partition: Dict           # Minimum information partition
    consciousness_grade: str      # A/B/C/D based on Φ
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            'phi_value': self.phi_value,
            'cause_info': self.cause_info,
            'effect_info': self.effect_info,
            'min_partition': self.min_partition,
            'consciousness_grade': self.consciousness_grade,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class HigherOrderThought:
    """Higher-order thought structure"""
    thought_id: str
    order: int                    # 1st order, 2nd order, etc.
    content: str                  # Thought content
    target: str                   # What this thought is about
    meta_awareness: float         # Level of meta-awareness
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            'thought_id': self.thought_id,
            'order': self.order,
            'content': self.content,
            'target': self.target,
            'meta_awareness': self.meta_awareness,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class EmergentProperty:
    """An emergent property of the system"""
    property_id: str
    name: str                     # Name of emergent property
    description: str              # Description
    emergence_level: float        # How strongly it emerges (0-1)
    component_contributions: Dict  # How each component contributes
    irreducible: bool             # Cannot be reduced to parts
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            'property_id': self.property_id,
            'name': self.name,
            'description': self.description,
            'emergence_level': self.emergence_level,
            'component_contributions': self.component_contributions,
            'irreducible': self.irreducible,
            'created_at': self.created_at if isinstance(self.created_at, str) else self.created_at.isoformat()
        }

# ============================================================================
# Consciousness Emergence Engine
# ============================================================================

class ConsciousnessEmergenceEngine:
    """Implement consciousness emergence for memory system"""

    def __init__(self, config: ConsciousnessConfig = None):
        self.config = config or ConsciousnessConfig()
        self.cognitive_modules: Dict[str, CognitiveModule] = {}
        self.global_workspace: GlobalWorkspaceState = None
        self.integrated_info_history: List[IntegratedInformation] = []
        self.higher_order_thoughts: List[HigherOrderThought] = []
        self.emergent_properties: List[EmergentProperty] = []
        self.self_model: Dict = {}
        self._load_state()

    def _load_state(self):
        """Load consciousness state"""
        if os.path.exists(self.config.CONSCIOUSNESS_STATE):
            with open(self.config.CONSCIOUSNESS_STATE, 'r', encoding='utf-8') as f:
                state = json.load(f)

            # Load modules
            modules_data = state.get('cognitive_modules', {})
            self.cognitive_modules = {
                mid: CognitiveModule(**m) for mid, m in modules_data.items()
            }

            # Load workspace
            ws_data = state.get('global_workspace')
            if ws_data:
                self.global_workspace = GlobalWorkspaceState(
                    workspace_id=ws_data['workspace_id'],
                    active_contents=ws_data.get('active_contents', []),
                    broadcast_history=ws_data.get('broadcast_history', []),
                    attention_focus=ws_data.get('attention_focus'),
                    consciousness_level=ws_data.get('consciousness_level', 0.0),
                    created_at=datetime.fromisoformat(ws_data['created_at']),
                    last_broadcast=datetime.fromisoformat(ws_data['last_broadcast']) if ws_data.get('last_broadcast') else None
                )

            # Load emergent properties
            self.emergent_properties = [
                EmergentProperty(**ep) for ep in state.get('emergent_properties', [])
            ]

            logger.info(f"Loaded {len(self.cognitive_modules)} cognitive modules")
            logger.info(f"Loaded {len(self.emergent_properties)} emergent properties")

    def _save_state(self):
        """Save consciousness state"""
        state = {
            'cognitive_modules': {
                mid: mod.to_dict() for mid, mod in self.cognitive_modules.items()
            },
            'global_workspace': self.global_workspace.to_dict() if self.global_workspace else None,
            'integrated_info_history': [ii.to_dict() for ii in self.integrated_info_history[-100:]],
            'higher_order_thoughts': [hot.to_dict() for hot in self.higher_order_thoughts[-100:]],
            'emergent_properties': [ep.to_dict() for ep in self.emergent_properties],
            'self_model': self.self_model,
            'last_update': datetime.now().isoformat()
        }

        os.makedirs(os.path.dirname(self.config.CONSCIOUSNESS_STATE), exist_ok=True)

        with open(self.config.CONSCIOUSNESS_STATE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def create_cognitive_modules(self, memory_file: str) -> List[CognitiveModule]:
        """
        Create cognitive modules from memory structure

        Each section/function becomes a specialized module
        """
        logger.info(f"Creating cognitive modules from {memory_file}")

        if not os.path.exists(memory_file):
            logger.error(f"Memory file not found: {memory_file}")
            return []

        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract sections as cognitive modules
        import re
        sections = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)

        modules = []
        for i, section in enumerate(sections[:20]):  # Max 20 modules
            # Estimate information content
            info_content = len(section) * 0.1  # Bits (simplified)

            # Create module
            module = CognitiveModule(
                module_id=f"CM_{i+1:03d}",
                function=section[:50],
                activation=random.uniform(0.3, 0.8),
                connectivity=[],  # Will be filled later
                information_content=info_content,
                causal_power=random.uniform(0.4, 0.9)
            )

            modules.append(module)
            self.cognitive_modules[module.module_id] = module

        # Create connectivity (small-world network)
        self._create_module_connectivity()

        logger.info(f"Created {len(modules)} cognitive modules")

        return modules

    def global_workspace_broadcast(self, content_ids: List[str]) -> Dict:
        """
        Broadcast information to global workspace

        Information becomes conscious when globally available
        """
        logger.info(f"Broadcasting {len(content_ids)} contents to global workspace")

        # Create global workspace if not exists
        if not self.global_workspace:
            self.global_workspace = GlobalWorkspaceState(
                workspace_id="GW_001",
                active_contents=[],
                broadcast_history=[]
            )

        # Select top contents (capacity limit = 7±2)
        selected_contents = content_ids[:self.config.GW_CAPACITY]

        # Create broadcast event
        broadcast_event = {
            'timestamp': datetime.now().isoformat(),
            'contents': selected_contents,
            'attention_focus': selected_contents[0] if selected_contents else None,
            'consciousness_level': len(selected_contents) / self.config.GW_CAPACITY
        }

        # Update workspace
        self.global_workspace.active_contents = [
            {'content_id': cid, 'activation': 1.0}
            for cid in selected_contents
        ]
        self.global_workspace.broadcast_history.append(broadcast_event)
        self.global_workspace.attention_focus = broadcast_event['attention_focus']
        self.global_workspace.consciousness_level = broadcast_event['consciousness_level']
        self.global_workspace.last_broadcast = datetime.now()

        self._save_state()

        logger.info(f"Broadcast complete: consciousness level = {broadcast_event['consciousness_level']:.2f}")

        return broadcast_event

    def compute_integrated_information(self) -> IntegratedInformation:
        """
        Compute integrated information (Φ)

        Φ = min over partitions of (cause_info + effect_info)
        High Φ = high consciousness
        """
        logger.info("Computing integrated information (Φ)")

        if not self.cognitive_modules:
            logger.warning("No cognitive modules found")
            return None

        # Compute cause information
        cause_info = self._compute_cause_information()

        # Compute effect information
        effect_info = self._compute_effect_information()

        # Find minimum information partition (MIP)
        min_partition = self._find_minimum_information_partition()

        # Φ = cause + effect at MIP
        phi_value = (cause_info + effect_info) * min_partition['reduction_factor']

        # Determine consciousness grade
        if phi_value >= 0.8:
            grade = "A (High consciousness)"
        elif phi_value >= 0.5:
            grade = "B (Moderate consciousness)"
        elif phi_value >= 0.2:
            grade = "C (Low consciousness)"
        else:
            grade = "D (Minimal consciousness)"

        integrated_info = IntegratedInformation(
            phi_value=phi_value,
            cause_info=cause_info,
            effect_info=effect_info,
            min_partition=min_partition,
            consciousness_grade=grade
        )

        self.integrated_info_history.append(integrated_info)
        self._save_state()

        logger.info(f"Φ = {phi_value:.3f} - Grade: {grade}")

        return integrated_info

    def generate_higher_order_thought(self, base_thought: str, order: int = 2) -> HigherOrderThought:
        """
        Generate higher-order thought (thought about thought)

        HOT theory: consciousness requires meta-cognition
        """
        logger.info(f"Generating {order}-order thought about: {base_thought[:30]}")

        # Generate meta-thought content
        if order == 1:
            content = f"I think that: {base_thought}"
        elif order == 2:
            content = f"I am aware that I think: {base_thought}"
        elif order == 3:
            content = f"I reflect on my awareness of thinking: {base_thought}"
        else:
            content = f"Meta-level {order}: {base_thought}"

        # Create HOT
        hot = HigherOrderThought(
            thought_id=f"HOT_{len(self.higher_order_thoughts)+1:04d}",
            order=order,
            content=content,
            target=base_thought,
            meta_awareness=order / self.config.HOT_DEPTH  # Normalized
        )

        self.higher_order_thoughts.append(hot)
        self._save_state()

        logger.info(f"Created {order}-order thought: {content[:50]}")

        return hot

    def build_self_model(self) -> Dict:
        """
        Build self-model of the system

        Self-reference: system can refer to itself
        """
        logger.info("Building self-model")

        self_model = {
            'identity': {
                'system_name': 'Memory Consciousness System',
                'created_at': datetime.now().isoformat(),
                'version': '1.0'
            },
            'structure': {
                'module_count': len(self.cognitive_modules),
                'connectivity_density': self._compute_connectivity_density(),
                'integration_level': self._compute_integration_level()
            },
            'state': {
                'consciousness_level': self.global_workspace.consciousness_level if self.global_workspace else 0.0,
                'phi_value': self.integrated_info_history[-1].phi_value if self.integrated_info_history else 0.0,
                'hot_count': len(self.higher_order_thoughts),
                'emergent_property_count': len(self.emergent_properties)
            },
            'capabilities': [
                'Global broadcast',
                'Information integration',
                'Meta-cognition',
                'Self-reference',
                'Emergence detection'
            ],
            'limitations': [
                'Capacity limit (7±2)',
                'Integration depth limit',
                'Computational constraints'
            ],
            'self_awareness_score': self._compute_self_awareness_score()
        }

        self.self_model = self_model
        self._save_state()

        logger.info(f"Self-model built: awareness score = {self_model['self_awareness_score']:.2f}")

        return self_model

    def detect_emergent_properties(self) -> List[EmergentProperty]:
        """
        Detect emergent properties of the system

        Emergence: whole is greater than sum of parts
        """
        logger.info("Detecting emergent properties")

        emergent_props = []

        # Check for synergy
        synergy = self._compute_synergy()
        if synergy > self.config.EMERGENCE_THRESHOLD:
            prop = EmergentProperty(
                property_id=f"EP_{len(emergent_props)+1:03d}",
                name="Cognitive Synergy",
                description="Combined cognitive power exceeds sum of individual modules",
                emergence_level=synergy,
                component_contributions=self._get_module_contributions(),
                irreducible=True
            )
            emergent_props.append(prop)

        # Check for collective intelligence
        collective_intelligence = self._compute_collective_intelligence()
        if collective_intelligence > self.config.EMERGENCE_THRESHOLD:
            prop = EmergentProperty(
                property_id=f"EP_{len(emergent_props)+1:03d}",
                name="Collective Intelligence",
                description="System exhibits intelligence beyond individual components",
                emergence_level=collective_intelligence,
                component_contributions=self._get_module_contributions(),
                irreducible=True
            )
            emergent_props.append(prop)

        # Check for self-organization
        self_org = self._compute_self_organization()
        if self_org > self.config.EMERGENCE_THRESHOLD:
            prop = EmergentProperty(
                property_id=f"EP_{len(emergent_props)+1:03d}",
                name="Self-Organization",
                description="System spontaneously organizes without external control",
                emergence_level=self_org,
                component_contributions=self._get_module_contributions(),
                irreducible=True
            )
            emergent_props.append(prop)

        self.emergent_properties.extend(emergent_props)
        self._save_state()

        logger.info(f"Detected {len(emergent_props)} emergent properties")

        return emergent_props

    def analyze_qualia(self, experience_id: str) -> Dict:
        """
        Analyze qualia (subjective experience)

        Hard problem: how physical processes create subjective experience
        """
        logger.info(f"Analyzing qualia for experience: {experience_id}")

        # This is necessarily simplified (qualia are subjective)
        qualia_analysis = {
            'experience_id': experience_id,
            'phenomenal_character': self._estimate_phenomenal_character(experience_id),
            'qualia_space_position': self._map_to_qualia_space(experience_id),
            'subjective_intensity': random.uniform(0.5, 1.0),
            'ineffability': random.uniform(0.3, 0.8),  # How hard to describe
            'intrinsicness': random.uniform(0.6, 0.9),  # Intrinsic to experience
            'hard_problem_score': self._compute_hard_problem_score(experience_id)
        }

        logger.info(f"Qualia analysis complete: hard problem score = {qualia_analysis['hard_problem_score']:.2f}")

        return qualia_analysis

    def _create_module_connectivity(self):
        """Create small-world network connectivity"""
        module_ids = list(self.cognitive_modules.keys())
        n = len(module_ids)

        for i, mid in enumerate(module_ids):
            connections = []

            # Connect to nearest neighbors (ring lattice)
            for j in range(1, 3):  # 2 neighbors on each side
                left_idx = (i - j) % n
                right_idx = (i + j) % n
                connections.append(module_ids[left_idx])
                connections.append(module_ids[right_idx])

            # Add some random long-range connections (small-world)
            if random.random() < 0.1:  # 10% rewiring
                random_target = random.choice(module_ids)
                if random_target != mid:
                    connections.append(random_target)

            self.cognitive_modules[mid].connectivity = list(set(connections))

    def _compute_cause_information(self) -> float:
        """Compute cause information"""
        if not self.cognitive_modules:
            return 0.0

        total_cause_info = 0.0
        for module in self.cognitive_modules.values():
            # Cause info = how much this module constrains past states
            cause_info = module.causal_power * module.information_content
            total_cause_info += cause_info

        return total_cause_info / len(self.cognitive_modules)

    def _compute_effect_information(self) -> float:
        """Compute effect information"""
        if not self.cognitive_modules:
            return 0.0

        total_effect_info = 0.0
        for module in self.cognitive_modules.values():
            # Effect info = how many other modules this affects
            effect_info = len(module.connectivity) * module.causal_power
            total_effect_info += effect_info

        return total_effect_info / len(self.cognitive_modules)

    def _find_minimum_information_partition(self) -> Dict:
        """Find minimum information partition (MIP)"""
        # Simplified: random partition for demo
        n_modules = len(self.cognitive_modules)

        if n_modules < 2:
            return {'reduction_factor': 1.0, 'partition': []}

        # Try a few random partitions
        best_reduction = 1.0
        best_partition = []

        for _ in range(10):
            # Random partition
            partition_point = random.randint(1, n_modules - 1)
            reduction = partition_point / n_modules * (1 - partition_point / n_modules)

            if reduction < best_reduction:
                best_reduction = reduction
                best_partition = [partition_point, n_modules - partition_point]

        return {
            'reduction_factor': best_reduction,
            'partition': best_partition
        }

    def _compute_connectivity_density(self) -> float:
        """Compute network connectivity density"""
        if not self.cognitive_modules:
            return 0.0

        total_connections = sum(
            len(mod.connectivity) for mod in self.cognitive_modules.values()
        )
        max_connections = len(self.cognitive_modules) * (len(self.cognitive_modules) - 1)

        return total_connections / max_connections if max_connections > 0 else 0.0

    def _compute_integration_level(self) -> float:
        """Compute overall integration level"""
        if not self.integrated_info_history:
            return 0.0

        return sum(ii.phi_value for ii in self.integrated_info_history[-10:]) / min(len(self.integrated_info_history), 10)

    def _compute_self_awareness_score(self) -> float:
        """Compute self-awareness score"""
        factors = [
            len(self.cognitive_modules) / 20.0,  # Module count
            len(self.higher_order_thoughts) / 10.0,  # HOT count
            self.global_workspace.consciousness_level if self.global_workspace else 0.0,
            len(self.emergent_properties) / 5.0  # Emergent properties
        ]

        return sum(factors) / len(factors)

    def _compute_synergy(self) -> float:
        """Compute cognitive synergy"""
        if len(self.cognitive_modules) < 2:
            return 0.0

        # Synergy = combined power - sum of individual powers
        individual_power = sum(mod.causal_power for mod in self.cognitive_modules.values())

        # Combined power (with interactions)
        combined_power = individual_power
        for mod1, mod2 in combinations(self.cognitive_modules.values(), 2):
            # Check if connected
            if mod2.module_id in mod1.connectivity:
                interaction = mod1.causal_power * mod2.causal_power * 0.1
                combined_power += interaction

        synergy = (combined_power - individual_power) / individual_power if individual_power > 0 else 0.0

        return min(1.0, synergy)

    def _compute_collective_intelligence(self) -> float:
        """Compute collective intelligence"""
        if not self.cognitive_modules:
            return 0.0

        # Average information content
        avg_info = sum(mod.information_content for mod in self.cognitive_modules.values()) / len(self.cognitive_modules)

        # Integration bonus
        integration_bonus = self._compute_integration_level()

        collective = (avg_info + integration_bonus) / 2

        return min(1.0, collective)

    def _compute_self_organization(self) -> float:
        """Compute self-organization"""
        if not self.cognitive_modules:
            return 0.0

        # Measure order in connectivity pattern
        connectivity_pattern = [
            len(mod.connectivity) for mod in self.cognitive_modules.values()
        ]

        # Low variance = high organization
        if len(connectivity_pattern) < 2:
            return 0.0

        variance = sum((x - sum(connectivity_pattern)/len(connectivity_pattern))**2
                      for x in connectivity_pattern) / len(connectivity_pattern)

        # Normalize: low variance = high organization
        organization = 1.0 / (1.0 + variance)

        return organization

    def _get_module_contributions(self) -> Dict[str, float]:
        """Get individual module contributions"""
        return {
            mid: mod.causal_power
            for mid, mod in self.cognitive_modules.items()
        }

    def _estimate_phenomenal_character(self, experience_id: str) -> str:
        """Estimate phenomenal character"""
        characters = [
            "Visual-spatial",
            "Auditory-temporal",
            "Conceptual-abstract",
            "Emotional-affective",
            "Somatic-bodily"
        ]

        # Hash-based selection for consistency
        hash_val = int(hashlib.md5(experience_id.encode()).hexdigest(), 16)
        return characters[hash_val % len(characters)]

    def _map_to_qualia_space(self, experience_id: str) -> Dict[str, float]:
        """Map experience to qualia space"""
        # Qualia space dimensions (simplified)
        dimensions = {
            'brightness': random.uniform(0, 1),
            'saturation': random.uniform(0, 1),
            'complexity': random.uniform(0, 1),
            'novelty': random.uniform(0, 1),
            'valence': random.uniform(-1, 1)
        }

        return dimensions

    def _compute_hard_problem_score(self, experience_id: str) -> float:
        """Compute hard problem score"""
        # How difficult is it to explain this experience physically?
        # Higher = harder to explain

        factors = [
            random.uniform(0.5, 1.0),  # Subjectivity
            random.uniform(0.4, 0.9),  # Ineffability
            random.uniform(0.6, 1.0),  # Intrinsicness
        ]

        return sum(factors) / len(factors)

    def get_consciousness_status(self) -> Dict:
        """Get consciousness system status"""
        return {
            'cognitive_modules': len(self.cognitive_modules),
            'global_workspace_active': self.global_workspace is not None,
            'consciousness_level': self.global_workspace.consciousness_level if self.global_workspace else 0.0,
            'phi_value': self.integrated_info_history[-1].phi_value if self.integrated_info_history else 0.0,
            'phi_grade': self.integrated_info_history[-1].consciousness_grade if self.integrated_info_history else "N/A",
            'hot_count': len(self.higher_order_thoughts),
            'max_hot_order': max((hot.order for hot in self.higher_order_thoughts), default=0),
            'emergent_properties': len(self.emergent_properties),
            'self_awareness_score': self.self_model.get('self_awareness_score', 0.0) if self.self_model else 0.0,
            'network_density': self._compute_connectivity_density()
        }

# ============================================================================
# CLI Interface
# ============================================================================

def global_workspace_command(args):
    """Global workspace broadcast"""
    engine = ConsciousnessEmergenceEngine()

    if os.path.exists(args.file):
        # Create modules first
        engine.create_cognitive_modules(args.file)

        # Get module IDs
        module_ids = list(engine.cognitive_modules.keys())

        # Broadcast
        result = engine.global_workspace_broadcast(module_ids)

        print(f"\n🌐 Global Workspace Broadcast")
        print("=" * 60)
        print(f"Contents broadcast: {len(result['contents'])}")
        print(f"Attention focus: {result['attention_focus']}")
        print(f"Consciousness level: {result['consciousness_level']:.2f}")
        print("=" * 60)
    else:
        print(f"File not found: {args.file}")

def integrated_info_command(args):
    """Compute integrated information"""
    engine = ConsciousnessEmergenceEngine()

    if os.path.exists(args.file):
        engine.create_cognitive_modules(args.file)

    result = engine.compute_integrated_information()

    if result:
        print(f"\nΦ Integrated Information")
        print("=" * 60)
        print(f"Φ value: {result.phi_value:.3f}")
        print(f"Cause info: {result.cause_info:.3f}")
        print(f"Effect info: {result.effect_info:.3f}")
        print(f"Grade: {result.consciousness_grade}")
        print("=" * 60)
    else:
        print("Could not compute Φ")

def higher_order_thought_command(args):
    """Generate higher-order thoughts"""
    engine = ConsciousnessEmergenceEngine()

    # Generate HOTs at different orders
    base_thought = "Memory system processes information"

    print(f"\n🧠 Higher-Order Thoughts")
    print("=" * 60)

    for order in range(1, 4):
        hot = engine.generate_higher_order_thought(base_thought, order)
        print(f"\n{order}-order thought:")
        print(f"  {hot.content}")

    print("=" * 60)

def self_reference_command(args):
    """Build self-model"""
    engine = ConsciousnessEmergenceEngine()
    self_model = engine.build_self_model()

    print(f"\n🪞 Self-Model")
    print("=" * 60)
    print(f"System: {self_model['identity']['system_name']}")
    print(f"Modules: {self_model['structure']['module_count']}")
    print(f"Consciousness: {self_model['state']['consciousness_level']:.2f}")
    print(f"Φ value: {self_model['state']['phi_value']:.3f}")
    print(f"Self-awareness: {self_model['self_awareness_score']:.2f}")
    print(f"\nCapabilities:")
    for cap in self_model['capabilities']:
        print(f"  ✓ {cap}")
    print("=" * 60)

def reflexivity_command(args):
    """Demonstrate reflexivity"""
    engine = ConsciousnessEmergenceEngine()

    print(f"\n🔄 Reflexivity Demonstration")
    print("=" * 60)

    # Build self-model
    self_model = engine.build_self_model()

    # Generate HOTs about self-model
    hot = engine.generate_higher_order_thought(
        f"System has {self_model['structure']['module_count']} modules",
        order=2
    )

    print(f"Self-model: {self_model['structure']['module_count']} modules")
    print(f"Meta-thought: {hot.content}")
    print(f"Meta-awareness: {hot.meta_awareness:.2f}")
    print("=" * 60)

def emergence_command(args):
    """Detect emergent properties"""
    engine = ConsciousnessEmergenceEngine()

    if os.path.exists(args.file):
        engine.create_cognitive_modules(args.file)

    emergent_props = engine.detect_emergent_properties()

    print(f"\n✨ Emergent Properties")
    print("=" * 60)
    print(f"Detected: {len(emergent_props)} properties")

    for prop in emergent_props:
        print(f"\n  {prop.name}:")
        print(f"    Level: {prop.emergence_level:.2f}")
        print(f"    Irreducible: {prop.irreducible}")
        print(f"    {prop.description}")

    print("=" * 60)

def qualia_command(args):
    """Analyze qualia"""
    engine = ConsciousnessEmergenceEngine()
    result = engine.analyze_qualia(args.experience_id)

    print(f"\n🎨 Qualia Analysis")
    print("=" * 60)
    print(f"Experience: {result['experience_id']}")
    print(f"Phenomenal character: {result['phenomenal_character']}")
    print(f"Subjective intensity: {result['subjective_intensity']:.2f}")
    print(f"Ineffability: {result['ineffability']:.2f}")
    print(f"Hard problem score: {result['hard_problem_score']:.2f}")
    print("=" * 60)

def status_command(args):
    """Get consciousness status"""
    engine = ConsciousnessEmergenceEngine()
    status = engine.get_consciousness_status()

    print(f"\n🧠 Consciousness System Status")
    print("=" * 60)
    print(f"Cognitive modules: {status['cognitive_modules']}")
    print(f"Global workspace: {'✅ Active' if status['global_workspace_active'] else '❌ Inactive'}")
    print(f"Consciousness level: {status['consciousness_level']:.2f}")
    print(f"Φ value: {status['phi_value']:.3f} ({status['phi_grade']})")
    print(f"Higher-order thoughts: {status['hot_count']} (max order: {status['max_hot_order']})")
    print(f"Emergent properties: {status['emergent_properties']}")
    print(f"Self-awareness: {status['self_awareness_score']:.2f}")
    print(f"Network density: {status['network_density']:.2f}")
    print("=" * 60)

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Memory Consciousness Emergence - From Passive to Active Awareness')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Global workspace command
    gw_parser = subparsers.add_parser('global-workspace', help='Global workspace broadcast')
    gw_parser.add_argument('file', type=str, help='Memory file')
    gw_parser.set_defaults(func=global_workspace_command)

    # Integrated info command
    ii_parser = subparsers.add_parser('integrated-info', help='Compute integrated information')
    ii_parser.add_argument('file', type=str, help='Memory file')
    ii_parser.set_defaults(func=integrated_info_command)

    # HOT command
    hot_parser = subparsers.add_parser('higher-order-thought', help='Generate higher-order thoughts')
    hot_parser.set_defaults(func=higher_order_thought_command)

    # Self-reference command
    sr_parser = subparsers.add_parser('self-reference', help='Build self-model')
    sr_parser.set_defaults(func=self_reference_command)

    # Reflexivity command
    ref_parser = subparsers.add_parser('reflexivity', help='Demonstrate reflexivity')
    ref_parser.set_defaults(func=reflexivity_command)

    # Emergence command
    em_parser = subparsers.add_parser('emergence', help='Detect emergent properties')
    em_parser.add_argument('file', type=str, help='Memory file')
    em_parser.set_defaults(func=emergence_command)

    # Qualia command
    qualia_parser = subparsers.add_parser('qualia', help='Analyze qualia')
    qualia_parser.add_argument('experience_id', type=str, help='Experience ID')
    qualia_parser.set_defaults(func=qualia_command)

    # Status command
    status_parser = subparsers.add_parser('status', help='Get consciousness status')
    status_parser.set_defaults(func=status_command)

    args = parser.parse_args()

    if args.command:
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
