#!/usr/bin/env python3
"""
Memory Neural Network - Synaptic Plasticity Learning System
============================================================
Transforms static memory storage into dynamic neural network with learning capability.

Key Concepts:
- Neurons: Individual memories or concepts
- Synapses: Associations between memories
- LTP (Long-Term Potentiation): Frequently used connections strengthen
- LTD (Long-Term Depression): Rarely used connections weaken
- STDP (Spike-Timing-Dependent Plasticity): Causal ordering of connections
- Hebbian Learning: "Neurons that fire together, wire together"

Usage:
    python memory_neural_network.py --build "MEMORY.md"
    python memory_neural_network.py --stimulate "query"  # Activate neurons
    python memory_neural_network.py --potentiate         # Strengthen pathways
    python memory_neural_network.py --prune              # Weaken unused connections
    python memory_neural_network.py --visualize          # Network visualization
"""

import os
import sys
import json
import math
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import networkx as nx

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
class NeuralConfig:
    """Neural network configuration"""
    
    # Learning parameters
    LTP_RATE: float = 0.1           # Long-term potentiation rate
    LTD_RATE: float = 0.05          # Long-term depression rate
    STDP_WINDOW: float = 0.02       # 20ms window for STDP (in seconds)
    HEAT_DECAY: float = 0.95        # Neural activity decay
    
    # Thresholds
    ACTIVATION_THRESHOLD: float = 0.5    # Min activation to "fire"
    PRUNING_THRESHOLD: float = 0.1       # Below this → prune connection
    SATURATION_THRESHOLD: float = 0.95   # Max connection strength
    
    # Network parameters
    INITIAL_WEIGHT: float = 0.5     # New synapse initial weight
    MAX_WEIGHT: float = 1.0         # Maximum synapse weight
    MIN_WEIGHT: float = 0.0         # Minimum synapse weight
    
    # Paths
    WORKSPACE: str = os.path.join(os.path.dirname(__file__), '..')
    NETWORK_STATE_FILE: str = os.path.join(WORKSPACE, 'data', 'neural_network_state.json')
    NETWORK_VISUALIZATION: str = os.path.join(WORKSPACE, 'data', 'neural_network.html')


# ============================================================================
# Neural Components
# ============================================================================

@dataclass
class Neuron:
    """Neuron - represents a memory or concept"""
    neuron_id: str
    content: str
    memory_source: str
    activation: float = 0.0      # Current activation level (0.0 - 1.0)
    threshold: float = 0.5       # Firing threshold
    bias: float = 0.0            # Bias term
    last_fired: Optional[datetime] = None
    fire_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'neuron_id': self.neuron_id,
            'content': self.content[:200],  # Truncate for storage
            'memory_source': self.memory_source,
            'activation': self.activation,
            'threshold': self.threshold,
            'bias': self.bias,
            'last_fired': self.last_fired.isoformat() if self.last_fired else None,
            'fire_count': self.fire_count,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Neuron':
        return cls(
            neuron_id=data['neuron_id'],
            content=data['content'],
            memory_source=data['memory_source'],
            activation=data['activation'],
            threshold=data['threshold'],
            bias=data['bias'],
            last_fired=datetime.fromisoformat(data['last_fired']) if data.get('last_fired') else None,
            fire_count=data.get('fire_count', 0),
            created_at=datetime.fromisoformat(data['created_at'])
        )
    
    def fire(self, timestamp: datetime = None):
        """Fire this neuron"""
        self.activation = 1.0
        self.last_fired = timestamp or datetime.now()
        self.fire_count += 1
    
    def decay(self, rate: float = 0.95):
        """Decay activation over time"""
        self.activation *= rate


@dataclass
class Synapse:
    """Synapse - connection between neurons"""
    synapse_id: str
    pre_neuron: str      # Source neuron ID
    post_neuron: str     # Target neuron ID
    weight: float = 0.5  # Connection strength (0.0 - 1.0)
    delay: float = 0.001  # Transmission delay (in seconds)
    last_transmission: Optional[datetime] = None
    transmission_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'synapse_id': self.synapse_id,
            'pre_neuron': self.pre_neuron,
            'post_neuron': self.post_neuron,
            'weight': self.weight,
            'delay': self.delay,
            'last_transmission': self.last_transmission.isoformat() if self.last_transmission else None,
            'transmission_count': self.transmission_count,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Synapse':
        return cls(
            synapse_id=data['synapse_id'],
            pre_neuron=data['pre_neuron'],
            post_neuron=data['post_neuron'],
            weight=data['weight'],
            delay=data['delay'],
            last_transmission=datetime.fromisoformat(data['last_transmission']) if data.get('last_transmission') else None,
            transmission_count=data.get('transmission_count', 0),
            created_at=datetime.fromisoformat(data['created_at'])
        )


# ============================================================================
# Memory Neural Network
# ============================================================================

class MemoryNeuralNetwork:
    """Neural network for memory with synaptic plasticity"""
    
    def __init__(self, config: NeuralConfig = None):
        self.config = config or NeuralConfig()
        self.neurons: Dict[str, Neuron] = {}
        self.synapses: Dict[str, Synapse] = {}
        self.graph = nx.DiGraph()  # NetworkX graph for analysis
        self._load_state()
    
    def _load_state(self):
        """Load network state"""
        if os.path.exists(self.config.NETWORK_STATE_FILE):
            with open(self.config.NETWORK_STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.neurons = {
                k: Neuron.from_dict(v) for k, v in state.get('neurons', {}).items()
            }
            self.synapses = {
                k: Synapse.from_dict(v) for k, v in state.get('synapses', {}).items()
            }
            
            # Rebuild graph
            self._rebuild_graph()
            
            logger.info(f"Loaded neural network: {len(self.neurons)} neurons, {len(self.synapses)} synapses")
        else:
            logger.info("Initialized new neural network")
    
    def _save_state(self):
        """Save network state"""
        state = {
            'neurons': {k: self.neurons[k].to_dict() for k in self.neurons},
            'synapses': {k: self.synapses[k].to_dict() for k in self.synapses}
        }
        
        os.makedirs(os.path.dirname(self.config.NETWORK_STATE_FILE), exist_ok=True)
        
        with open(self.config.NETWORK_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def _rebuild_graph(self):
        """Rebuild NetworkX graph from synapses"""
        self.graph.clear()
        
        for neuron_id in self.neurons:
            self.graph.add_node(neuron_id)
        
        for synapse in self.synapses.values():
            self.graph.add_edge(
                synapse.pre_neuron,
                synapse.post_neuron,
                weight=synapse.weight,
                delay=synapse.delay
            )
    
    def _create_synapse_id(self, pre_neuron: str, post_neuron: str) -> str:
        """Generate unique synapse ID"""
        return f"SYN_{hashlib.md5(f'{pre_neuron}_{post_neuron}'.encode()).hexdigest()[:8]}"
    
    def build_from_memory(self, memory_file: str) -> Tuple[int, int]:
        """
        Build neural network from memory file
        
        Process:
        1. Extract insights/concepts as neurons
        2. Create synapses based on co-occurrence and semantic similarity
        3. Initialize weights based on quality scores
        """
        logger.info(f"Building neural network from {memory_file}...")
        
        neurons_created = 0
        synapses_created = 0
        
        try:
            from memory_distiller_v2 import MemoryDistiller, DistillerConfig
            
            distiller = MemoryDistiller(DistillerConfig())
            insights = distiller.extract_insights(memory_file)
            
            # Create neurons from insights
            neuron_ids = []
            for insight in insights:
                neuron_id = f"N_{hashlib.md5(insight['content'].encode()).hexdigest()[:8]}"
                
                if neuron_id not in self.neurons:
                    neuron = Neuron(
                        neuron_id=neuron_id,
                        content=insight['content'],
                        memory_source=memory_file,
                        activation=0.0,
                        threshold=0.5
                    )
                    self.neurons[neuron_id] = neuron
                    neurons_created += 1
                
                neuron_ids.append(neuron_id)
            
            # Create synapses based on co-occurrence (insights from same file)
            for i, pre_id in enumerate(neuron_ids):
                for post_id in neuron_ids[i+1:]:
                    synapse_id = self._create_synapse_id(pre_id, post_id)
                    
                    if synapse_id not in self.synapses:
                        synapse = Synapse(
                            synapse_id=synapse_id,
                            pre_neuron=pre_id,
                            post_neuron=post_id,
                            weight=self.config.INITIAL_WEIGHT,
                            delay=0.001
                        )
                        self.synapses[synapse_id] = synapse
                        synapses_created += 1
            
            self._rebuild_graph()
            self._save_state()
            
            logger.info(f"Built network: {neurons_created} neurons, {synapses_created} synapses")
        
        except ImportError as e:
            logger.warning(f"Failed to build network: {e}")
        
        return neurons_created, synapses_created
    
    def stimulate(self, query: str) -> List[str]:
        """
        Stimulate network with query and return activated neurons
        
        Process:
        1. Find neurons matching query (semantic similarity)
        2. Activate matching neurons
        3. Propagate activation through synapses
        4. Return fired neurons
        """
        logger.info(f"Stimulating network with query: {query}")
        
        # Reset all activations
        for neuron in self.neurons.values():
            neuron.decay(self.config.HEAT_DECAY)
        
        # Find matching neurons (simple keyword matching for now)
        query_words = set(query.lower().split())
        matched_neurons = []
        
        for neuron in self.neurons.values():
            content_words = set(neuron.content.lower().split())
            overlap = len(query_words & content_words)
            
            if overlap > 0:
                similarity = overlap / max(len(query_words), len(content_words))
                neuron.activation = min(1.0, neuron.activation + similarity)
                
                if neuron.activation >= neuron.threshold:
                    neuron.fire()
                    matched_neurons.append(neuron.neuron_id)
        
        # Propagate activation through synapses
        self._propagate_activation()
        
        # Collect all fired neurons
        fired_neurons = [
            n.neuron_id for n in self.neurons.values()
            if n.last_fired and (datetime.now() - n.last_fired).total_seconds() < 1.0
        ]
        
        logger.info(f"Stimulation complete: {len(fired_neurons)} neurons fired")
        
        return fired_neurons
    
    def _propagate_activation(self, iterations: int = 3):
        """Propagate activation through synaptic connections"""
        for _ in range(iterations):
            for synapse in self.synapses.values():
                pre_neuron = self.neurons.get(synapse.pre_neuron)
                post_neuron = self.neurons.get(synapse.post_neuron)
                
                if pre_neuron and post_neuron and pre_neuron.activation > 0:
                    # Transmit signal
                    signal = pre_neuron.activation * synapse.weight
                    
                    if signal >= post_neuron.threshold:
                        post_neuron.activation = min(1.0, post_neuron.activation + signal)
                        post_neuron.fire()
                        synapse.transmission_count += 1
                        synapse.last_transmission = datetime.now()
    
    def apply_ltp(self, neuron_pairs: List[Tuple[str, str]]):
        """
        Apply Long-Term Potentiation to strengthen frequently used connections
        
        Hebbian learning: "Neurons that fire together, wire together"
        """
        logger.info(f"Applying LTP to {len(neuron_pairs)} connections...")
        
        strengthened = 0
        
        for pre_id, post_id in neuron_pairs:
            synapse_id = self._create_synapse_id(pre_id, post_id)
            
            if synapse_id in self.synapses:
                synapse = self.synapses[synapse_id]
                
                # Strengthen synapse
                old_weight = synapse.weight
                synapse.weight = min(
                    self.config.MAX_WEIGHT,
                    synapse.weight + self.config.LTP_RATE
                )
                
                if synapse.weight > old_weight:
                    strengthened += 1
        
        self._save_state()
        
        logger.info(f"LTP complete: {strengthened} synapses strengthened")
    
    def apply_ltd(self, inactive_duration: timedelta = timedelta(days=7)):
        """
        Apply Long-Term Depression to weaken unused connections
        """
        logger.info(f"Applying LTD to inactive synapses...")
        
        now = datetime.now()
        weakened = 0
        pruned = 0
        
        for synapse in list(self.synapses.values()):
            # Check if synapse has been inactive
            if synapse.last_transmission:
                inactive_time = now - synapse.last_transmission
                
                if inactive_time > inactive_duration:
                    old_weight = synapse.weight
                    synapse.weight = max(
                        self.config.MIN_WEIGHT,
                        synapse.weight - self.config.LTD_RATE
                    )
                    
                    if synapse.weight < old_weight:
                        weakened += 1
                    
                    # Prune if below threshold
                    if synapse.weight < self.config.PRUNING_THRESHOLD:
                        del self.synapses[synapse_id]
                        pruned += 1
        
        self._rebuild_graph()
        self._save_state()
        
        logger.info(f"LTD complete: {weakened} weakened, {pruned} pruned")
    
    def apply_stdp(self, spike_times: Dict[str, datetime]):
        """
        Apply Spike-Timing-Dependent Plasticity
        
        If pre-neuron fires before post-neuron → strengthen (causal)
        If pre-neuron fires after post-neuron → weaken (anti-causal)
        """
        logger.info(f"Applying STDP...")
        
        modified = 0
        
        for synapse in self.synapses.values():
            pre_time = spike_times.get(synapse.pre_neuron)
            post_time = spike_times.get(synapse.post_neuron)
            
            if pre_time and post_time:
                delta_t = (post_time - pre_time).total_seconds()
                
                if abs(delta_t) < self.config.STDP_WINDOW:
                    if delta_t > 0:
                        # Pre before post → strengthen (LTP)
                        synapse.weight = min(
                            self.config.MAX_WEIGHT,
                            synapse.weight + self.config.LTP_RATE * math.exp(-delta_t / self.config.STDP_WINDOW)
                        )
                    else:
                        # Post before pre → weaken (LTD)
                        synapse.weight = max(
                            self.config.MIN_WEIGHT,
                            synapse.weight - self.config.LTD_RATE * math.exp(delta_t / self.config.STDP_WINDOW)
                        )
                    
                    modified += 1
        
        self._save_state()
        
        logger.info(f"STDP complete: {modified} synapses modified")
    
    def prune_unused(self, min_fire_count: int = 1):
        """Prune neurons that have never fired"""
        logger.info(f"Pruning unused neurons...")
        
        pruned = 0
        
        for neuron_id in list(self.neurons.keys()):
            neuron = self.neurons[neuron_id]
            
            if neuron.fire_count < min_fire_count:
                del self.neurons[neuron_id]
                
                # Remove associated synapses
                synapse_ids = [
                    sid for sid, syn in self.synapses.items()
                    if syn.pre_neuron == neuron_id or syn.post_neuron == neuron_id
                ]
                
                for sid in synapse_ids:
                    del self.synapses[sid]
                
                pruned += 1
        
        self._rebuild_graph()
        self._save_state()
        
        logger.info(f"Pruning complete: {pruned} neurons removed")
    
    def get_network_stats(self) -> Dict:
        """Get network statistics"""
        self._rebuild_graph()
        
        stats = {
            'total_neurons': len(self.neurons),
            'total_synapses': len(self.synapses),
            'avg_degree': 0.0,
            'density': 0.0,
            'avg_clustering': 0.0,
            'total_fires': sum(n.fire_count for n in self.neurons.values()),
            'avg_activation': sum(n.activation for n in self.neurons.values()) / max(len(self.neurons), 1),
            'strongest_synapse': 0.0,
            'weakest_synapse': 1.0
        }
        
        if self.graph.number_of_nodes() > 0:
            stats['avg_degree'] = sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes()
            stats['density'] = nx.density(self.graph)
            
            try:
                stats['avg_clustering'] = nx.average_clustering(self.graph)
            except:
                stats['avg_clustering'] = 0.0
        
        if self.synapses:
            weights = [s.weight for s in self.synapses.values()]
            stats['strongest_synapse'] = max(weights)
            stats['weakest_synapse'] = min(weights)
        
        return stats
    
    def visualize(self):
        """Generate HTML visualization of neural network"""
        logger.info("Generating network visualization...")
        
        # Use PyVis for interactive visualization
        try:
            from pyvis.network import Network
            
            net = Network(height='800px', width='100%', bgcolor='#222222', font_color='white')
            
            # Add nodes
            for neuron_id, neuron in self.neurons.items():
                size = 10 + 20 * neuron.activation  # Size by activation
                color = f'#{int(255 * neuron.activation):02x}{int(255 * (1 - neuron.activation)):02x}00'
                
                net.add_node(
                    neuron_id,
                    label=neuron_id,
                    title=neuron.content[:200],
                    size=size,
                    color=color
                )
            
            # Add edges
            for synapse in self.synapses.values():
                net.add_edge(
                    synapse.pre_neuron,
                    synapse.post_neuron,
                    value=synapse.weight * 10,  # Width by weight
                    title=f'Weight: {synapse.weight:.2f}'
                )
            
            # Save visualization
            net.save_graph(self.config.NETWORK_VISUALIZATION)
            
            logger.info(f"Visualization saved: {self.config.NETWORK_VISUALIZATION}")
        
        except ImportError:
            logger.warning("PyVis not available, generating simple HTML visualization")
            self._generate_simple_visualization()
    
    def _generate_simple_visualization(self):
        """Generate simple HTML visualization without PyVis"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Memory Neural Network</title>
    <style>
        body {{ font-family: Arial; background: #1a1a2e; color: white; }}
        .neuron {{ display: inline-block; margin: 5px; padding: 10px; background: #16213e; border-radius: 5px; }}
        .synapse {{ color: #0f3460; }}
    </style>
</head>
<body>
    <h1>Memory Neural Network</h1>
    <p>Neurons: {len(self.neurons)} | Synapses: {len(self.synapses)}</p>
    <div id="network">
        {''.join(f'<div class="neuron">{n.neuron_id} (activation: {n.activation:.2f})</div>' for n in list(self.neurons.values())[:50])}
    </div>
</body>
</html>
"""
        
        with open(self.config.NETWORK_VISUALIZATION, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Simple visualization saved: {self.config.NETWORK_VISUALIZATION}")


# ============================================================================
# CLI Interface
# ============================================================================

def build_command(args):
    """Build network from memory"""
    network = MemoryNeuralNetwork()
    neurons, synapses = network.build_from_memory(args.file)
    
    print(f"\n🧠 Neural Network Built")
    print("=" * 60)
    print(f"Neurons created: {neurons}")
    print(f"Synapses created: {synapses}")
    print("=" * 60)


def stimulate_command(args):
    """Stimulate network"""
    network = MemoryNeuralNetwork()
    fired = network.stimulate(args.query)
    
    print(f"\n⚡ Network Stimulation")
    print("=" * 60)
    print(f"Query: {args.query}")
    print(f"Neurons fired: {len(fired)}")
    for neuron_id in fired[:10]:
        print(f"  - {neuron_id}")
    if len(fired) > 10:
        print(f"  ... and {len(fired) - 10} more")
    print("=" * 60)


def potentiate_command(args):
    """Apply LTP"""
    network = MemoryNeuralNetwork()
    
    # Find co-activated neurons
    co_activated = []
    for synapse in network.synapses.values():
        pre = network.neurons.get(synapse.pre_neuron)
        post = network.neurons.get(synapse.post_neuron)
        
        if pre and post and pre.fire_count > 0 and post.fire_count > 0:
            co_activated.append((synapse.pre_neuron, synapse.post_neuron))
    
    network.apply_ltp(co_activated)
    
    print(f"\n💪 Long-Term Potentiation Applied")
    print("=" * 60)
    print(f"Connections strengthened: {len(co_activated)}")
    print("=" * 60)


def prune_command(args):
    """Apply LTD and prune"""
    network = MemoryNeuralNetwork()
    network.apply_ltd()
    network.prune_unused()
    
    stats = network.get_network_stats()
    
    print(f"\n✂️ Pruning Complete")
    print("=" * 60)
    print(f"Total neurons: {stats['total_neurons']}")
    print(f"Total synapses: {stats['total_synapses']}")
    print(f"Average activation: {stats['avg_activation']:.2f}")
    print("=" * 60)


def visualize_command(args):
    """Visualize network"""
    network = MemoryNeuralNetwork()
    network.visualize()
    
    print(f"\n📊 Network Visualization Generated")
    print("=" * 60)
    print(f"File: {network.config.NETWORK_VISUALIZATION}")
    print("=" * 60)


def status_command(args):
    """Get network status"""
    network = MemoryNeuralNetwork()
    stats = network.get_network_stats()
    
    print(f"\n🧠 Neural Network Status")
    print("=" * 60)
    print(f"Total neurons: {stats['total_neurons']}")
    print(f"Total synapses: {stats['total_synapses']}")
    print(f"Average degree: {stats['avg_degree']:.2f}")
    print(f"Network density: {stats['density']:.4f}")
    print(f"Avg clustering: {stats['avg_clustering']:.2f}")
    print(f"Total fires: {stats['total_fires']}")
    print(f"Avg activation: {stats['avg_activation']:.2f}")
    print(f"Strongest synapse: {stats['strongest_synapse']:.2f}")
    print(f"Weakest synapse: {stats['weakest_synapse']:.2f}")
    print("=" * 60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Neural Network - Synaptic Plasticity Learning System')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build network from memory')
    build_parser.add_argument('file', type=str, help='Memory file')
    build_parser.set_defaults(func=build_command)
    
    # Stimulate command
    stimulate_parser = subparsers.add_parser('stimulate', help='Stimulate network')
    stimulate_parser.add_argument('query', type=str, help='Stimulation query')
    stimulate_parser.set_defaults(func=stimulate_command)
    
    # Potentiate command
    potentiate_parser = subparsers.add_parser('potentiate', help='Apply LTP')
    potentiate_parser.set_defaults(func=potentiate_command)
    
    # Prune command
    prune_parser = subparsers.add_parser('prune', help='Apply LTD and prune')
    prune_parser.set_defaults(func=prune_command)
    
    # Visualize command
    visualize_parser = subparsers.add_parser('visualize', help='Visualize network')
    visualize_parser.set_defaults(func=visualize_command)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get network status')
    status_parser.set_defaults(func=status_command)
    
    args = parser.parse_args()
    
    if args.command:
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
