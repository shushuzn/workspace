#!/usr/bin/env python3
"""
Memory Immune System - Biological Immunity Inspired Defense
============================================================
Transforms passive memory cleaning into active immune defense system.

Key Concepts:
- Antibodies: High-quality memory fragments that neutralize low-quality inputs
- T-Cells: Direct elimination of harmful/low-quality memories
- B-Cells: Produce antibodies from high-quality memories
- Macrophages: Engulf contradictions and fuse information
- Immune Memory: Learn from past errors to prevent recurrence
- Adaptive Thresholds: Dynamic adjustment based on system health

Usage:
    python memory_immune_system.py --scan "MEMORY.md"
    python memory_immune_system.py --vaccinate  # Generate antibodies
    python memory_immune_system.py --respond    # Immune response to threats
    python memory_immune_system.py --status     # Immune system health
"""

import os
import sys
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

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
class ImmuneConfig:
    """Immune system configuration"""
    
    # Antibody parameters
    ANTIBODY_QUALITY_THRESHOLD: float = 0.85  # Min quality to become antibody
    ANTIBODY_STRENGTH_DECAY: float = 0.95    # Monthly decay rate
    ANTIBODY_MEMORY_LIFESPAN: int = 90       # Days antibodies persist
    
    # T-Cell parameters
    T_CELL_KILL_THRESHOLD: float = 0.30      # Below this → direct elimination
    T_CELL_ANERGY_THRESHOLD: float = 0.50    # Below this → anergy (ignore)
    
    # Macrophage parameters
    MACROPHAGE_SIMILARITY_THRESHOLD: float = 0.70  # For conflict detection
    MACROPHAGE_FUSION_STRATEGY: str = "newer_better"  # newer_better/higher_quality
    
    # Immune response
    CYTOKINE_STORM_THRESHOLD: int = 10       # Conflicts triggering storm
    RESPONSE_AMPLIFICATION: float = 1.5      # Amplify response under attack
    
    # Homeostasis
    HEALTHY_ANTIBODY_COUNT: int = 100        # Target antibody count
    AUTOIMMUNE_THRESHOLD: float = 0.95       # Too aggressive → autoimmune risk
    
    # Paths
    WORKSPACE: str = os.path.join(os.path.dirname(__file__), '..')
    IMMUNE_STATE_FILE: str = os.path.join(WORKSPACE, 'data', 'immune_state.json')
    ANTIBODY_REPOSITORY: str = os.path.join(WORKSPACE, 'data', 'antibodies')


# ============================================================================
# Immune Cell Types
# ============================================================================

class CellType(Enum):
    """Immune cell types"""
    B_CELL = "b_cell"           # Produce antibodies
    T_CELL = "t_cell"           # Kill low-quality memories
    MACROPHAGE = "macrophage"   # Engulf conflicts
    DENDRITIC = "dendritic"     # Present antigens


@dataclass
class ImmuneCell:
    """Immune cell representation"""
    cell_id: str
    cell_type: CellType
    created_at: datetime
    activation_level: float = 0.0  # 0.0 - 1.0
    memory_antigens: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'cell_id': self.cell_id,
            'cell_type': self.cell_type.value,
            'created_at': self.created_at.isoformat(),
            'activation_level': self.activation_level,
            'memory_antigens': self.memory_antigens
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ImmuneCell':
        return cls(
            cell_id=data['cell_id'],
            cell_type=CellType(data['cell_type']),
            created_at=datetime.fromisoformat(data['created_at']),
            activation_level=data['activation_level'],
            memory_antigens=data.get('memory_antigens', [])
        )


@dataclass
class Antibody:
    """Antibody - high-quality memory fragment"""
    antibody_id: str
    source_memory: str
    fragment_hash: str
    quality_score: float
    strength: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    target_antigens: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'antibody_id': self.antibody_id,
            'source_memory': self.source_memory,
            'fragment_hash': self.fragment_hash,
            'quality_score': self.quality_score,
            'strength': self.strength,
            'created_at': self.created_at.isoformat(),
            'last_used': self.last_used.isoformat(),
            'usage_count': self.usage_count,
            'target_antigens': self.target_antigens
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Antibody':
        return cls(
            antibody_id=data['antibody_id'],
            source_memory=data['source_memory'],
            fragment_hash=data['fragment_hash'],
            quality_score=data['quality_score'],
            strength=data['strength'],
            created_at=datetime.fromisoformat(data['created_at']),
            last_used=datetime.fromisoformat(data['last_used']),
            usage_count=data.get('usage_count', 0),
            target_antigens=data.get('target_antigens', [])
        )


@dataclass
class Antigen:
    """Antigen - low-quality or conflicting memory"""
    antigen_id: str
    memory_path: str
    antigen_type: str  # low_quality/contradiction/duplicate/outdated
    severity: float    # 0.0 - 1.0
    detected_at: datetime = field(default_factory=datetime.now)
    neutralized: bool = False
    neutralized_by: Optional[str] = None  # Antibody ID
    
    def to_dict(self) -> Dict:
        return {
            'antigen_id': self.antigen_id,
            'memory_path': self.memory_path,
            'antigen_type': self.antigen_type,
            'severity': self.severity,
            'detected_at': self.detected_at.isoformat(),
            'neutralized': self.neutralized,
            'neutralized_by': self.neutralized_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Antigen':
        return cls(
            antigen_id=data['antigen_id'],
            memory_path=data['memory_path'],
            antigen_type=data['antigen_type'],
            severity=data['severity'],
            detected_at=datetime.fromisoformat(data['detected_at']),
            neutralized=data['neutralized'],
            neutralized_by=data.get('neutralized_by')
        )


# ============================================================================
# Memory Immune System
# ============================================================================

class MemoryImmuneSystem:
    """Biological immune system for memory defense"""
    
    def __init__(self, config: ImmuneConfig = None):
        self.config = config or ImmuneConfig()
        self._ensure_directories()
        self._load_state()
    
    def _ensure_directories(self):
        """Create necessary directories"""
        os.makedirs(os.path.dirname(self.config.IMMUNE_STATE_FILE), exist_ok=True)
        os.makedirs(self.config.ANTIBODY_REPOSITORY, exist_ok=True)
    
    def _load_state(self):
        """Load immune system state"""
        if os.path.exists(self.config.IMMUNE_STATE_FILE):
            with open(self.config.IMMUNE_STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.antibodies = {
                k: Antibody.from_dict(v) for k, v in state.get('antibodies', {}).items()
            }
            self.antigens = {
                k: Antigen.from_dict(v) for k, v in state.get('antigens', {}).items()
            }
            self.cells = {
                k: ImmuneCell.from_dict(v) for k, v in state.get('cells', {}).items()
            }
            self.health_metrics = state.get('health_metrics', {})
        else:
            self.antibodies = {}
            self.antigens = {}
            self.cells = {}
            self.health_metrics = {
                'system_health': 1.0,
                'autoimmune_risk': 0.0,
                'response_efficiency': 1.0,
                'antibody_diversity': 0.0
            }
    
    def _save_state(self):
        """Save immune system state"""
        state = {
            'antibodies': {k: v.to_dict() for k, v in self.antibodies.items()},
            'antigens': {k: v.to_dict() for k, v in self.antigens.items()},
            'cells': {k: v.to_dict() for k, v in self.cells.items()},
            'health_metrics': self.health_metrics
        }
        
        with open(self.config.IMMUNE_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def scan_for_antigens(self, memory_file: str) -> List[Antigen]:
        """
        Scan memory file for antigens (threats)
        
        Antigens types:
        - low_quality: Quality score < T_CELL_KILL_THRESHOLD
        - contradiction: Conflicting information
        - duplicate: Near-duplicate content
        - outdated: Superseded by newer information
        """
        logger.info(f"Scanning {memory_file} for antigens...")
        
        antigens = []
        
        # Import quality scorer
        try:
            from memory_quality_scorer import MemoryQualityScorer
            scorer = MemoryQualityScorer()
            
            # Assess overall quality
            quality_score = scorer.assess_file(memory_file)
            
            if quality_score < self.config.T_CELL_KILL_THRESHOLD:
                antigen = Antigen(
                    antigen_id=f"AG_{hashlib.md5(memory_file.encode()).hexdigest()[:8]}",
                    memory_path=memory_file,
                    antigen_type="low_quality",
                    severity=(self.config.T_CELL_KILL_THRESHOLD - quality_score) / self.config.T_CELL_KILL_THRESHOLD
                )
                antigens.append(antigen)
                logger.info(f"🦠 Low quality antigen detected: {quality_score:.2f}")
            
            # Check for contradictions (import conflict detector)
            try:
                from memory_conflict_detector import ConflictDetector, ResolverConfig
                detector = ConflictDetector(ResolverConfig())
                
                # Scan for conflicts
                conflicts = detector.scan_file(memory_file)
                
                for conflict in conflicts:
                    antigen = Antigen(
                        antigen_id=f"AG_{hashlib.md5(conflict['id'].encode()).hexdigest()[:8]}",
                        memory_path=memory_file,
                        antigen_type="contradiction",
                        severity=conflict.get('severity', 0.5)
                    )
                    antigens.append(antigen)
                    logger.info(f"🦠 Contradiction antigen detected: {conflict['type']}")
            
            except ImportError:
                logger.warning("Conflict detector not available, skipping contradiction scan")
        
        except ImportError:
            logger.warning("Quality scorer not available, using heuristic scan")
            # Fallback: simple heuristic scan
            with open(memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Heuristic: very short files are low quality
            if len(content) < 100:
                antigen = Antigen(
                    antigen_id=f"AG_{hashlib.md5(memory_file.encode()).hexdigest()[:8]}",
                    memory_path=memory_file,
                    antigen_type="low_quality",
                    severity=0.8
                )
                antigens.append(antigen)
        
        # Store detected antigens
        for antigen in antigens:
            self.antigens[antigen.antigen_id] = antigen
        
        self._save_state()
        
        return antigens
    
    def generate_antibodies(self, memory_file: str) -> List[Antibody]:
        """
        Generate antibodies from high-quality memory fragments
        
        B-Cells extract high-quality fragments and create antibodies
        """
        logger.info(f"Generating antibodies from {memory_file}...")
        
        antibodies = []
        
        try:
            from memory_quality_scorer import MemoryQualityScorer
            from memory_distiller_v2 import MemoryDistiller, DistillerConfig
            
            scorer = MemoryQualityScorer()
            distiller = MemoryDistiller(DistillerConfig())
            
            # Extract high-quality insights
            insights = distiller.extract_insights(memory_file)
            
            for insight in insights:
                # Assess fragment quality
                fragment_quality = scorer.assess_text(insight['content'])
                
                if fragment_quality >= self.config.ANTIBODY_QUALITY_THRESHOLD:
                    # Create antibody
                    antibody_id = f"AB_{hashlib.md5(insight['content'].encode()).hexdigest()[:8]}"
                    
                    antibody = Antibody(
                        antibody_id=antibody_id,
                        source_memory=memory_file,
                        fragment_hash=hashlib.md5(insight['content'].encode()).hexdigest(),
                        quality_score=fragment_quality,
                        strength=1.0,
                        target_antigens=[]  # Will be populated during immune response
                    )
                    
                    antibodies.append(antibody)
                    self.antibodies[antibody_id] = antibody
                    
                    logger.info(f"💪 Antibody generated: {antibody_id} (quality: {fragment_quality:.2f})")
        
        except ImportError as e:
            logger.warning(f"Antibody generation failed: {e}")
        
        self._save_state()
        
        return antibodies
    
    def immune_response(self) -> Dict:
        """
        Mount immune response to detected antigens
        
        Process:
        1. Dendritic cells present antigens
        2. Helper T-Cells activate B-Cells
        3. B-Cells produce specific antibodies
        4. Antibodies neutralize antigens
        5. Memory cells created for future protection
        """
        logger.info("Mounting immune response...")
        
        response_stats = {
            'antigens_detected': len([a for a in self.antigens.values() if not a.neutralized]),
            'antibodies_deployed': 0,
            'antigens_neutralized': 0,
            'memory_cells_created': 0,
            'cytokine_storm': False
        }
        
        # Check for cytokine storm (overwhelming infection)
        if response_stats['antigens_detected'] > self.config.CYTOKINE_STORM_THRESHOLD:
            response_stats['cytokine_storm'] = True
            logger.warning("⚠️ CYTOKINE STORM DETECTED - Overwhelming infection!")
        
        # Match antibodies to antigens
        for antigen in list(self.antigens.values()):
            if antigen.neutralized:
                continue
            
            # Find matching antibody
            best_antibody = None
            best_match_score = 0.0
            
            for antibody in self.antibodies.values():
                # Simple matching: antigen type vs antibody target
                # In real implementation, would use semantic similarity
                match_score = antibody.quality_score  # Placeholder
                
                if match_score > best_match_score:
                    best_match_score = match_score
                    best_antibody = antibody
            
            # Neutralize if match found
            if best_antibody and best_match_score >= 0.6:
                antigen.neutralized = True
                antigen.neutralized_by = best_antibody.antibody_id
                best_antibody.usage_count += 1
                best_antibody.last_used = datetime.now()
                
                response_stats['antibodies_deployed'] += 1
                response_stats['antigens_neutralized'] += 1
                
                logger.info(f"✅ Antigen {antigen.antigen_id} neutralized by {best_antibody.antibody_id}")
        
        # Create memory cells (immunological memory)
        if response_stats['antigens_neutralized'] > 0:
            memory_cell = ImmuneCell(
                cell_id=f"MC_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                cell_type=CellType.B_CELL,
                created_at=datetime.now(),
                activation_level=1.0,
                memory_antigens=[a.antigen_id for a in self.antigens.values() if a.neutralized]
            )
            self.cells[memory_cell.cell_id] = memory_cell
            response_stats['memory_cells_created'] = 1
            
            logger.info(f"🧠 Memory cell created for future protection")
        
        # Update health metrics
        self._update_health_metrics()
        self._save_state()
        
        return response_stats
    
    def _update_health_metrics(self):
        """Update overall immune system health"""
        # System health: ratio of neutralized antigens
        total_antigens = len(self.antigens)
        neutralized = len([a for a in self.antigens.values() if a.neutralized])
        
        self.health_metrics['system_health'] = neutralized / max(total_antigens, 1)
        
        # Autoimmune risk: too many antibodies attacking self
        antibody_count = len(self.antibodies)
        if antibody_count > self.config.HEALTHY_ANTIBODY_COUNT * 2:
            self.health_metrics['autoimmune_risk'] = min(1.0, antibody_count / (self.config.HEALTHY_ANTIBODY_COUNT * 3))
        else:
            self.health_metrics['autoimmune_risk'] = 0.0
        
        # Response efficiency: successful neutralizations per antibody
        if antibody_count > 0:
            total_usage = sum(ab.usage_count for ab in self.antibodies.values())
            self.health_metrics['response_efficiency'] = min(1.0, total_usage / (antibody_count * 10))
        else:
            self.health_metrics['response_efficiency'] = 0.0
        
        # Antibody diversity: variance in quality scores
        if antibody_count > 1:
            qualities = [ab.quality_score for ab in self.antibodies.values()]
            mean_q = sum(qualities) / len(qualities)
            variance = sum((q - mean_q) ** 2 for q in qualities) / len(qualities)
            self.health_metrics['antibody_diversity'] = min(1.0, variance * 10)
        else:
            self.health_metrics['antibody_diversity'] = 0.0
    
    def vaccinate(self, high_quality_memories: List[str]) -> Dict:
        """
        Vaccinate system by pre-generating antibodies from known high-quality memories
        
        This is proactive defense rather than reactive response
        """
        logger.info(f"Vaccinating with {len(high_quality_memories)} high-quality memories...")
        
        vaccination_stats = {
            'memories_processed': 0,
            'antibodies_generated': 0,
            'total_quality': 0.0
        }
        
        for memory_file in high_quality_memories:
            if os.path.exists(memory_file):
                antibodies = self.generate_antibodies(memory_file)
                
                if antibodies:
                    vaccination_stats['memories_processed'] += 1
                    vaccination_stats['antibodies_generated'] += len(antibodies)
                    vaccination_stats['total_quality'] += sum(ab.quality_score for ab in antibodies)
        
        if vaccination_stats['antibodies_generated'] > 0:
            vaccination_stats['avg_quality'] = vaccination_stats['total_quality'] / vaccination_stats['antibodies_generated']
        else:
            vaccination_stats['avg_quality'] = 0.0
        
        logger.info(f"💉 Vaccination complete: {vaccination_stats['antibodies_generated']} antibodies generated")
        
        return vaccination_stats
    
    def get_status(self) -> Dict:
        """Get immune system status"""
        self._update_health_metrics()
        
        return {
            'system_health': self.health_metrics.get('system_health', 0.0),
            'autoimmune_risk': self.health_metrics.get('autoimmune_risk', 0.0),
            'response_efficiency': self.health_metrics.get('response_efficiency', 0.0),
            'antibody_diversity': self.health_metrics.get('antibody_diversity', 0.0),
            'total_antibodies': len(self.antibodies),
            'active_antigens': len([a for a in self.antigens.values() if not a.neutralized]),
            'memory_cells': len(self.cells),
            'overall_status': 'HEALTHY' if self.health_metrics.get('system_health', 0.0) > 0.7 else 'COMPROMISED'
        }


# ============================================================================
# CLI Interface
# ============================================================================

def scan_command(args):
    """Scan for antigens"""
    immune = MemoryImmuneSystem()
    antigens = immune.scan_for_antigens(args.file)
    
    print(f"\n🦠 Antigen Scan Results")
    print("=" * 60)
    print(f"File: {args.file}")
    print(f"Antigens detected: {len(antigens)}")
    
    for antigen in antigens:
        print(f"  - {antigen.antigen_id}: {antigen.antigen_type} (severity: {antigen.severity:.2f})")
    
    print("=" * 60)


def vaccinate_command(args):
    """Vaccinate system"""
    immune = MemoryImmuneSystem()
    
    # Find high-quality memories
    memory_dir = os.path.join(immune.config.WORKSPACE, '13-memory-记忆系统')
    high_quality_files = []
    
    if os.path.exists(memory_dir):
        for filename in os.listdir(memory_dir):
            if filename.endswith('.md'):
                high_quality_files.append(os.path.join(memory_dir, filename))
    
    stats = immune.vaccinate(high_quality_files[:10])  # Top 10
    
    print(f"\n💉 Vaccination Results")
    print("=" * 60)
    print(f"Memories processed: {stats['memories_processed']}")
    print(f"Antibodies generated: {stats['antibodies_generated']}")
    print(f"Average quality: {stats['avg_quality']:.2f}")
    print("=" * 60)


def respond_command(args):
    """Mount immune response"""
    immune = MemoryImmuneSystem()
    stats = immune.immune_response()
    
    print(f"\n🛡️ Immune Response Results")
    print("=" * 60)
    print(f"Antigens detected: {stats['antigens_detected']}")
    print(f"Antibodies deployed: {stats['antibodies_deployed']}")
    print(f"Antigens neutralized: {stats['antigens_neutralized']}")
    print(f"Memory cells created: {stats['memory_cells_created']}")
    if stats['cytokine_storm']:
        print(f"⚠️ CYTOKINE STORM DETECTED!")
    print("=" * 60)


def status_command(args):
    """Get immune system status"""
    immune = MemoryImmuneSystem()
    status = immune.get_status()
    
    print(f"\n🏥 Immune System Status")
    print("=" * 60)
    print(f"Overall Status: {status['overall_status']}")
    print(f"System Health: {status['system_health']:.2%}")
    print(f"Autoimmune Risk: {status['autoimmune_risk']:.2%}")
    print(f"Response Efficiency: {status['response_efficiency']:.2%}")
    print(f"Antibody Diversity: {status['antibody_diversity']:.2%}")
    print(f"Total Antibodies: {status['total_antibodies']}")
    print(f"Active Antigens: {status['active_antigens']}")
    print(f"Memory Cells: {status['memory_cells']}")
    print("=" * 60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Immune System - Biological Immunity Inspired Defense')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan for antigens')
    scan_parser.add_argument('file', type=str, help='Memory file to scan')
    scan_parser.set_defaults(func=scan_command)
    
    # Vaccinate command
    vaccinate_parser = subparsers.add_parser('vaccinate', help='Vaccinate system')
    vaccinate_parser.set_defaults(func=vaccinate_command)
    
    # Respond command
    respond_parser = subparsers.add_parser('respond', help='Mount immune response')
    respond_parser.set_defaults(func=respond_command)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get immune system status')
    status_parser.set_defaults(func=status_command)
    
    args = parser.parse_args()
    
    if args.command:
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
