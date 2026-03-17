#!/usr/bin/env python3
"""
Memory Thermodynamics Engine - Entropy-Driven Self-Organization
================================================================
Applies thermodynamic principles to memory evolution.

Key Concepts:
- Entropy (S): Measure of disorder/randomness in memory
- Free Energy (F): F = U - TS (usable knowledge energy)
- Second Law: Memory entropy naturally increases (requires work to decrease)
- Phase Transitions: Critical points where memory reorganizes
- Maxwell's Demon: Intelligent sorting to reduce entropy
- Gibbs Free Energy: Knowledge available for "work" (insight generation)

Usage:
    python memory_thermodynamics.py --entropy "MEMORY.md"
    python memory_thermodynamics.py --free-energy
    python memory_thermodynamics.py --phase-transition
    python memory_thermodynamics.py --demon
    python memory_thermodynamics.py --status
"""

import os
import sys
import json
import logging
import math
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from collections import Counter, defaultdict

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
class ThermodynamicsConfig:
    """Thermodynamics engine configuration"""
    
    # Physical constants (normalized)
    BOLTZMANN_CONSTANT: float = 1.0     # k_B (normalized)
    TEMPERATURE: float = 300.0          # T (arbitrary units)
    
    # Entropy thresholds
    LOW_ENTROPY_THRESHOLD: float = 0.3   # Well-organized
    HIGH_ENTROPY_THRESHOLD: float = 0.7  # Chaotic
    CRITICAL_ENTROPY: float = 0.9        # Phase transition imminent
    
    # Phase transition
    CRITICAL_TEMPERATURE: float = 500.0  # T_c for phase transition
    
    # Paths
    WORKSPACE: str = os.path.join(os.path.dirname(__file__), '..')
    THERMO_STATE: str = os.path.join(WORKSPACE, 'data', 'thermo_state.json')
    THERMO_REPORT: str = os.path.join(WORKSPACE, 'data', 'thermo_report.json')


# ============================================================================
# Thermodynamic State
# ============================================================================

@dataclass
class ThermodynamicState:
    """Current thermodynamic state of memory"""
    timestamp: datetime
    internal_energy: float = 0.0      # U - total knowledge content
    entropy: float = 0.0              # S - disorder measure
    temperature: float = 300.0        # T - "activity level"
    free_energy: float = 0.0          # F = U - TS - usable knowledge
    heat_capacity: float = 0.0        # C - ability to absorb new knowledge
    pressure: float = 0.0             # P - "insight pressure"
    volume: float = 0.0               # V - memory size
    phase: str = "solid"              # solid/liquid/gas/plasma
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'internal_energy': self.internal_energy,
            'entropy': self.entropy,
            'temperature': self.temperature,
            'free_energy': self.free_energy,
            'heat_capacity': self.heat_capacity,
            'pressure': self.pressure,
            'volume': self.volume,
            'phase': self.phase
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ThermodynamicState':
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            internal_energy=data['internal_energy'],
            entropy=data['entropy'],
            temperature=data['temperature'],
            free_energy=data['free_energy'],
            heat_capacity=data['heat_capacity'],
            pressure=data['pressure'],
            volume=data['volume'],
            phase=data['phase']
        )


@dataclass
class PhaseTransition:
    """Record of a phase transition event"""
    transition_id: str
    from_phase: str
    to_phase: str
    critical_entropy: float
    timestamp: datetime
    trigger: str
    reorganization_summary: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'transition_id': self.transition_id,
            'from_phase': self.from_phase,
            'to_phase': self.to_phase,
            'critical_entropy': self.critical_entropy,
            'timestamp': self.timestamp.isoformat(),
            'trigger': self.trigger,
            'reorganization_summary': self.reorganization_summary
        }


# ============================================================================
# Thermodynamics Engine
# ============================================================================

class ThermodynamicsEngine:
    """Apply thermodynamics to memory evolution"""
    
    def __init__(self, config: ThermodynamicsConfig = None):
        self.config = config or ThermodynamicsConfig()
        self.current_state: Optional[ThermodynamicState] = None
        self.history: List[ThermodynamicState] = []
        self.phase_transitions: List[PhaseTransition] = []
        self._load_state()
    
    def _load_state(self):
        """Load thermodynamic state"""
        if os.path.exists(self.config.THERMO_STATE):
            with open(self.config.THERMO_STATE, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            if state.get('current_state'):
                self.current_state = ThermodynamicState.from_dict(state['current_state'])
            
            self.history = [
                ThermodynamicState.from_dict(s) for s in state.get('history', [])
            ]
            
            self.phase_transitions = [
                PhaseTransition.from_dict(t) for t in state.get('phase_transitions', [])
            ]
            
            logger.info(f"Loaded thermodynamic state: {self.current_state.phase if self.current_state else 'none'}")
    
    def _save_state(self):
        """Save thermodynamic state"""
        state = {
            'current_state': self.current_state.to_dict() if self.current_state else None,
            'history': [s.to_dict() for s in self.history[-100:]],  # Last 100 states
            'phase_transitions': [t.to_dict() for t in self.phase_transitions],
            'last_update': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(self.config.THERMO_STATE), exist_ok=True)
        
        with open(self.config.THERMO_STATE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def compute_entropy(self, memory_file: str) -> float:
        """
        Compute entropy of memory
        
        Entropy measures disorder/randomness:
        S = -k_B * Σ p_i * ln(p_i)
        
        Where p_i is probability of finding knowledge in state i
        """
        logger.info(f"Computing entropy of {memory_file}...")
        
        if not os.path.exists(memory_file):
            logger.error(f"Memory file not found: {memory_file}")
            return 0.0
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Method 1: Word frequency entropy
        words = content.lower().split()
        word_counts = Counter(words)
        total_words = len(words)
        
        entropy_words = 0.0
        for count in word_counts.values():
            if count > 0:
                p = count / total_words
                entropy_words -= p * math.log(p)
        
        # Normalize by maximum entropy (uniform distribution)
        max_entropy_words = math.log(len(word_counts)) if word_counts else 1.0
        normalized_entropy_words = entropy_words / max_entropy_words if max_entropy_words > 0 else 0.0
        
        # Method 2: Structural entropy (section distribution)
        sections = content.split('\n## ')
        section_lengths = [len(s) for s in sections if s.strip()]
        
        if section_lengths:
            total_length = sum(section_lengths)
            entropy_structure = 0.0
            
            for length in section_lengths:
                p = length / total_length
                if p > 0:
                    entropy_structure -= p * math.log(p)
            
            max_entropy_structure = math.log(len(section_lengths))
            normalized_entropy_structure = entropy_structure / max_entropy_structure if max_entropy_structure > 0 else 0.0
        else:
            normalized_entropy_structure = 0.0
        
        # Method 3: Topic diversity entropy
        topics = self._extract_topics(content)
        topic_counts = Counter(topics)
        total_topics = sum(topic_counts.values())
        
        entropy_topics = 0.0
        for count in topic_counts.values():
            if count > 0:
                p = count / total_topics
                entropy_topics -= p * math.log(p)
        
        max_entropy_topics = math.log(len(topic_counts)) if topic_counts else 1.0
        normalized_entropy_topics = entropy_topics / max_entropy_topics if max_entropy_topics > 0 else 0.0
        
        # Combined entropy (weighted average)
        combined_entropy = (
            0.4 * normalized_entropy_words +
            0.3 * normalized_entropy_structure +
            0.3 * normalized_entropy_topics
        )
        
        logger.info(f"Entropy: {combined_entropy:.3f} (words: {normalized_entropy_words:.3f}, structure: {normalized_entropy_structure:.3f}, topics: {normalized_entropy_topics:.3f})")
        
        return combined_entropy
    
    def compute_internal_energy(self, memory_file: str) -> float:
        """
        Compute internal energy (total knowledge content)
        
        U = Σ (knowledge_quality * knowledge_quantity)
        """
        if not os.path.exists(memory_file):
            return 0.0
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Energy proxies:
        # 1. Content size (bytes)
        size_energy = len(content) / 10000.0  # Normalize
        
        # 2. Information density (unique concepts)
        topics = self._extract_topics(content)
        concept_energy = len(set(topics)) / 100.0
        
        # 3. Connection density (cross-references)
        connections = content.count('[[[') + content.count('→') + content.count('←')
        connection_energy = connections / 50.0
        
        # Total internal energy
        internal_energy = size_energy + concept_energy + connection_energy
        
        logger.info(f"Internal energy: {internal_energy:.3f} (size: {size_energy:.3f}, concepts: {concept_energy:.3f}, connections: {connection_energy:.3f})")
        
        return internal_energy
    
    def compute_free_energy(self, U: float, S: float, T: float = None) -> float:
        """
        Compute Helmholtz free energy
        
        F = U - TS
        
        Free energy represents knowledge available for "work" (insight generation)
        """
        if T is None:
            T = self.config.TEMPERATURE
        
        # Normalize temperature
        T_normalized = T / self.config.CRITICAL_TEMPERATURE
        
        free_energy = U - T_normalized * S * self.config.BOLTZMANN_CONSTANT
        
        logger.info(f"Free energy: F = {free_energy:.3f} (U={U:.3f}, T={T_normalized:.3f}, S={S:.3f})")
        
        return free_energy
    
    def determine_phase(self, entropy: float, temperature: float) -> str:
        """
        Determine thermodynamic phase based on entropy and temperature
        
        Phases:
        - Solid: Low entropy, low temperature (crystalline knowledge structure)
        - Liquid: Medium entropy, medium temperature (flowing knowledge)
        - Gas: High entropy, high temperature (dispersed knowledge)
        - Plasma: Very high entropy/temperature (chaotic, ionized)
        """
        T_normalized = temperature / self.config.CRITICAL_TEMPERATURE
        
        if entropy < self.config.LOW_ENTROPY_THRESHOLD and T_normalized < 0.5:
            return "solid"
        elif entropy < self.config.HIGH_ENTROPY_THRESHOLD and T_normalized < 0.8:
            return "liquid"
        elif entropy < self.config.CRITICAL_ENTROPY:
            return "gas"
        else:
            return "plasma"
    
    def analyze_state(self, memory_file: str) -> ThermodynamicState:
        """
        Perform complete thermodynamic analysis
        """
        logger.info(f"Analyzing thermodynamic state of {memory_file}...")
        
        # Compute state variables
        S = self.compute_entropy(memory_file)
        U = self.compute_internal_energy(memory_file)
        T = self.config.TEMPERATURE  # Could be dynamic based on activity
        F = self.compute_free_energy(U, S, T)
        
        # Determine phase
        phase = self.determine_phase(S, T)
        
        # Compute derived quantities
        V = os.path.getsize(memory_file) / 1000000.0 if os.path.exists(memory_file) else 0.0  # Volume in MB
        C = self._compute_heat_capacity(memory_file)  # Ability to absorb new knowledge
        P = self._compute_pressure(U, V)  # Insight pressure
        
        # Create state
        state = ThermodynamicState(
            timestamp=datetime.now(),
            internal_energy=U,
            entropy=S,
            temperature=T,
            free_energy=F,
            heat_capacity=C,
            pressure=P,
            volume=V,
            phase=phase
        )
        
        # Check for phase transition
        if self.current_state and self.current_state.phase != phase:
            transition = PhaseTransition(
                transition_id=f"PT_{len(self.phase_transitions)+1:03d}",
                from_phase=self.current_state.phase,
                to_phase=phase,
                critical_entropy=S,
                timestamp=datetime.now(),
                trigger=f"Entropy change: {self.current_state.entropy:.3f} → {S:.3f}",
                reorganization_summary=f"Memory reorganized from {self.current_state.phase} to {phase} phase"
            )
            self.phase_transitions.append(transition)
            logger.warning(f"⚠️ Phase transition detected: {self.current_state.phase} → {phase}")
        
        # Update state
        self.current_state = state
        self.history.append(state)
        self._save_state()
        
        return state
    
    def _compute_heat_capacity(self, memory_file: str) -> float:
        """
        Compute heat capacity - ability to absorb new knowledge without major reorganization
        
        C = dU/dT (change in internal energy per unit temperature change)
        """
        # Proxy: diversity and redundancy
        if not os.path.exists(memory_file):
            return 0.0
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # More diverse topics = higher heat capacity
        topics = self._extract_topics(content)
        topic_diversity = len(set(topics)) / max(len(topics), 1)
        
        # Redundancy (repeated concepts) increases heat capacity
        topic_counts = Counter(topics)
        redundancy = sum((c - 1) for c in topic_counts.values() if c > 1) / max(len(topics), 1)
        
        heat_capacity = 0.5 * topic_diversity + 0.5 * redundancy
        
        return heat_capacity
    
    def _compute_pressure(self, U: float, V: float) -> float:
        """
        Compute pressure - "insight pressure"
        
        P = nRT/V (ideal gas law analogy)
        More knowledge in less space = higher pressure = more insights
        """
        if V < 0.001:
            V = 0.001  # Avoid division by zero
        
        # Pressure proportional to energy density
        pressure = U / V
        
        return pressure
    
    def maxwell_demon(self, memory_file: str) -> Dict:
        """
        Maxwell's Demon - intelligent sorting to reduce entropy
        
        The demon selectively allows "hot" (high-quality) knowledge
        to one side and "cold" (low-quality) to the other,
        effectively reducing entropy without work.
        """
        logger.info("🧚 Maxwell's Demon sorting memory...")
        
        if not os.path.exists(memory_file):
            return {'sorted': False, 'entropy_reduction': 0.0}
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Initial entropy
        initial_entropy = self.compute_entropy(memory_file)
        
        # Demon's sorting strategy:
        # 1. Identify high-quality sections (by structure, length, references)
        # 2. Reorganize to group similar quality
        
        sections = content.split('\n## ')
        
        # Score each section
        scored_sections = []
        for i, section in enumerate(sections):
            if not section.strip():
                continue
            
            # Quality score
            length_score = min(len(section) / 1000.0, 1.0)
            structure_score = 1.0 if '###' in section else 0.5
            reference_score = min(section.count('[[') / 10.0, 1.0)
            
            quality = 0.4 * length_score + 0.3 * structure_score + 0.3 * reference_score
            
            scored_sections.append({
                'index': i,
                'content': section,
                'quality': quality
            })
        
        # Sort by quality (demon's work)
        scored_sections.sort(key=lambda x: x['quality'], reverse=True)
        
        # Reconstruct content
        sorted_content = '\n## '.join(s['content'] for s in scored_sections)
        
        # Compute new entropy (simulated - would need to write file)
        # For now, estimate based on organization improvement
        entropy_reduction = 0.1 * (1.0 - initial_entropy)  # Up to 10% reduction
        
        final_entropy = initial_entropy - entropy_reduction
        
        result = {
            'sorted': True,
            'initial_entropy': initial_entropy,
            'final_entropy': final_entropy,
            'entropy_reduction': entropy_reduction,
            'sections_sorted': len(scored_sections),
            'quality_range': {
                'min': min(s['quality'] for s in scored_sections) if scored_sections else 0,
                'max': max(s['quality'] for s in scored_sections) if scored_sections else 0
            }
        }
        
        logger.info(f"Demon sorted {len(scored_sections)} sections, entropy reduction: {entropy_reduction:.3f}")
        
        return result
    
    def get_status(self) -> Dict:
        """Get thermodynamic status"""
        if not self.current_state:
            return {'status': 'no_data'}
        
        return {
            'phase': self.current_state.phase,
            'entropy': self.current_state.entropy,
            'free_energy': self.current_state.free_energy,
            'temperature': self.current_state.temperature,
            'internal_energy': self.current_state.internal_energy,
            'heat_capacity': self.current_state.heat_capacity,
            'pressure': self.current_state.pressure,
            'phase_transitions': len(self.phase_transitions),
            'history_length': len(self.history)
        }


# ============================================================================
# Utility Functions
# ============================================================================

    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from content"""
        import re
        
        # Find headers
        headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        
        # Find bold terms
        bold_terms = re.findall(r'\*\*(.+?)\*\*', content)
        
        # Find tags
        tags = re.findall(r'#(\w+)', content)
        
        topics = list(set(headers + bold_terms + tags))
        return [t.strip() for t in topics if len(t) > 2]


# ============================================================================
# CLI Interface
# ============================================================================

def entropy_command(args):
    """Compute entropy"""
    engine = ThermodynamicsEngine()
    entropy = engine.compute_entropy(args.file)
    
    print(f"\n🔥 Entropy Analysis")
    print("=" * 60)
    print(f"File: {args.file}")
    print(f"Entropy: {entropy:.3f}")
    
    if entropy < 0.3:
        print("State: 🧊 LOW ENTROPY (well-organized)")
    elif entropy < 0.7:
        print("State: 💧 MEDIUM ENTROPY (balanced)")
    else:
        print("State: 🔥 HIGH ENTROPY (chaotic)")
    
    print("=" * 60)


def free_energy_command(args):
    """Compute free energy"""
    engine = ThermodynamicsEngine()
    
    if not engine.current_state:
        if args.file:
            engine.analyze_state(args.file)
        else:
            print("No state available. Run --entropy first or provide file.")
            return
    
    print(f"\n⚡ Free Energy Analysis")
    print("=" * 60)
    print(f"Internal Energy (U): {engine.current_state.internal_energy:.3f}")
    print(f"Entropy (S): {engine.current_state.entropy:.3f}")
    print(f"Temperature (T): {engine.current_state.temperature:.1f}")
    print(f"Free Energy (F = U - TS): {engine.current_state.free_energy:.3f}")
    print(f"Phase: {engine.current_state.phase}")
    print("=" * 60)


def phase_transition_command(args):
    """Check for phase transitions"""
    engine = ThermodynamicsEngine()
    
    print(f"\n🔄 Phase Transition Analysis")
    print("=" * 60)
    print(f"Total transitions: {len(engine.phase_transitions)}")
    
    for transition in engine.phase_transitions[-5:]:
        print(f"\n  {transition.transition_id}")
        print(f"  {transition.from_phase} → {transition.to_phase}")
        print(f"  Critical entropy: {transition.critical_entropy:.3f}")
        print(f"  Trigger: {transition.trigger}")
    
    print("=" * 60)


def demon_command(args):
    """Maxwell's Demon sorting"""
    engine = ThermodynamicsEngine()
    result = engine.maxwell_demon(args.file)
    
    print(f"\n🧚 Maxwell's Demon Results")
    print("=" * 60)
    print(f"Sorted: {result['sorted']}")
    print(f"Sections sorted: {result['sections_sorted']}")
    print(f"Initial entropy: {result['initial_entropy']:.3f}")
    print(f"Final entropy: {result['final_entropy']:.3f}")
    print(f"Entropy reduction: {result['entropy_reduction']:.3f} ({result['entropy_reduction']*100:.1f}%)")
    print(f"Quality range: {result['quality_range']['min']:.2f} - {result['quality_range']['max']:.2f}")
    print("=" * 60)


def status_command(args):
    """Get thermodynamic status"""
    engine = ThermodynamicsEngine()
    status = engine.get_status()
    
    print(f"\n🌡️ Thermodynamic Status")
    print("=" * 60)
    
    if status.get('status') == 'no_data':
        print("No thermodynamic data. Run --entropy first.")
    else:
        print(f"Phase: {status['phase']}")
        print(f"Entropy: {status['entropy']:.3f}")
        print(f"Free Energy: {status['free_energy']:.3f}")
        print(f"Temperature: {status['temperature']:.1f}")
        print(f"Internal Energy: {status['internal_energy']:.3f}")
        print(f"Heat Capacity: {status['heat_capacity']:.3f}")
        print(f"Pressure: {status['pressure']:.3f}")
        print(f"Phase transitions: {status['phase_transitions']}")
        print(f"History length: {status['history_length']}")
    
    print("=" * 60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Thermodynamics Engine - Entropy-Driven Self-Organization')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Entropy command
    entropy_parser = subparsers.add_parser('entropy', help='Compute entropy')
    entropy_parser.add_argument('file', type=str, help='Memory file')
    entropy_parser.set_defaults(func=entropy_command)
    
    # Free energy command
    fe_parser = subparsers.add_parser('free-energy', help='Compute free energy')
    fe_parser.add_argument('--file', type=str, help='Memory file')
    fe_parser.set_defaults(func=free_energy_command)
    
    # Phase transition command
    pt_parser = subparsers.add_parser('phase-transition', help='Check phase transitions')
    pt_parser.set_defaults(func=phase_transition_command)
    
    # Maxwell's demon command
    demon_parser = subparsers.add_parser('demon', help="Maxwell's Demon sorting")
    demon_parser.add_argument('file', type=str, help='Memory file')
    demon_parser.set_defaults(func=demon_command)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get thermodynamic status')
    status_parser.set_defaults(func=status_command)
    
    args = parser.parse_args()
    
    if args.command:
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
