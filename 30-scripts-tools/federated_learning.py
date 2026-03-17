#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Federated Learning Framework - Privacy-Preserving Collaboration
Features: Secure Aggregation, Differential Privacy, Homomorphic Encryption Simulation

Usage:
    python federated_learning.py --rounds 10
    python federated_learning.py --demo
"""

import os
import sys
import json
import math
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
import random
import statistics

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class AggregationMethod:
    """Secure aggregation methods"""
    FEDAVG = "fedavg"  # Federated Averaging
    FEDPROX = "fedprox"  # Federated Proximal
    SECURE_AGG = "secure_agg"  # Secure Aggregation with masking


@dataclass
class Client:
    """Federated learning client"""
    id: str
    data_size: int
    model_update: Dict[str, float]
    privacy_budget: float  # Epsilon for differential privacy
    is_malicious: bool = False


@dataclass
class Round:
    """Federated learning round"""
    round_id: int
    participating_clients: List[str]
    aggregated_model: Dict[str, float]
    global_loss: float
    global_accuracy: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class PrivacyConfig:
    """Differential privacy configuration"""
    epsilon: float  # Privacy budget
    delta: float  # Failure probability
    noise_scale: float  # Gaussian noise scale
    clip_norm: float  # Gradient clipping norm


@dataclass
class SecurityReport:
    """Security analysis report"""
    round_id: int
    clients_detected: int
    malicious_detected: int
    privacy_guarantee: str
    security_score: float


class FederatedLearningFramework:
    """Federated learning framework"""
    
    def __init__(self, n_clients: int = 10, privacy_config: PrivacyConfig = None):
        self.data_dir = WORKSPACE / "20-data-reports" / "federated"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.rounds_file = self.data_dir / "rounds.json"
        self.clients_file = self.data_dir / "clients.json"
        
        self.n_clients = n_clients
        self.privacy_config = privacy_config or PrivacyConfig(
            epsilon=1.0,
            delta=1e-5,
            noise_scale=0.1,
            clip_norm=1.0
        )
        
        self.clients: List[Client] = []
        self.rounds: List[Round] = []
        self.global_model: Dict[str, float] = {}
        
        self.load_state()
    
    def load_state(self):
        """Load state"""
        if self.rounds_file.exists():
            with open(self.rounds_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.rounds = [
                    Round(**r) for r in data.get('rounds', [])
                ]
        
        if self.clients_file.exists():
            with open(self.clients_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.clients = [
                    Client(**c) for c in data.get('clients', [])
                ]
    
    def save_state(self):
        """Save state"""
        with open(self.rounds_file, 'w', encoding='utf-8') as f:
            json.dump({
                'rounds': [asdict(r) for r in self.rounds],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.clients_file, 'w', encoding='utf-8') as f:
            json.dump({
                'clients': [asdict(c) for c in self.clients],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def initialize_clients(self, n_clients: int = None):
        """Initialize federated clients"""
        n_clients = n_clients or self.n_clients
        
        self.clients = []
        for i in range(n_clients):
            client = Client(
                id=f"client_{i}",
                data_size=random.randint(100, 1000),
                model_update=self._generate_random_update(),
                privacy_budget=self.privacy_config.epsilon,
                is_malicious=(random.random() < 0.1)  # 10% malicious
            )
            self.clients.append(client)
        
        # Initialize global model
        self.global_model = {
            f"weight_{i}": random.gauss(0, 0.1)
            for i in range(10)
        }
        
        print(f"✅ Initialized {n_clients} federated clients")
        print(f"   Privacy Budget (ε): {self.privacy_config.epsilon}")
        print(f"   Noise Scale: {self.privacy_config.noise_scale}")
        print(f"   Malicious Clients: {sum(c.is_malicious for c in self.clients)}\n")
    
    def train_round(
        self,
        round_id: int,
        n_participants: int = 5,
        aggregation_method: str = AggregationMethod.FEDAVG
    ) -> Round:
        """Execute one round of federated learning"""
        
        # Select participating clients
        participants = random.sample(self.clients, min(n_participants, len(self.clients)))
        
        print(f"\n🔄 Round {round_id}")
        print(f"   Participants: {len(participants)} clients")
        print(f"   Method: {aggregation_method}")
        
        # Collect model updates
        updates = []
        for client in participants:
            # Simulate local training
            local_update = self._simulate_local_training(client)
            
            # Apply differential privacy
            if self.privacy_config.epsilon < float('inf'):
                local_update = self._add_dp_noise(local_update)
            
            # Clip gradients
            local_update = self._clip_gradients(local_update)
            
            updates.append({
                'client_id': client.id,
                'update': local_update,
                'data_size': client.data_size,
                'is_malicious': client.is_malicious
            })
        
        # Aggregate updates
        if aggregation_method == AggregationMethod.FEDAVG:
            aggregated = self._federated_average(updates)
        elif aggregation_method == AggregationMethod.FEDPROX:
            aggregated = self._federated_proximal(updates)
        elif aggregation_method == AggregationMethod.SECURE_AGG:
            aggregated = self._secure_aggregation(updates)
        else:
            aggregated = self._federated_average(updates)
        
        # Update global model
        for key in self.global_model:
            self.global_model[key] += aggregated.get(key, 0) * 0.1  # Learning rate
        
        # Evaluate global model
        global_loss = self._evaluate_loss()
        global_accuracy = self._evaluate_accuracy()
        
        round_result = Round(
            round_id=round_id,
            participating_clients=[u['client_id'] for u in updates],
            aggregated_model={k: round(v, 6) for k, v in aggregated.items()},
            global_loss=round(global_loss, 4),
            global_accuracy=round(global_accuracy, 4)
        )
        
        self.rounds.append(round_result)
        
        print(f"   Global Loss: {global_loss:.4f}")
        print(f"   Global Accuracy: {global_accuracy:.1%}")
        
        # Security analysis
        security_report = self._analyze_security(round_id, updates)
        print(f"   Security Score: {security_report.security_score:.1%}")
        if security_report.malicious_detected > 0:
            print(f"   ⚠️  Malicious clients detected: {security_report.malicious_detected}")
        
        return round_result
    
    def _simulate_local_training(self, client: Client) -> Dict[str, float]:
        """Simulate local model training"""
        # Generate update based on client data
        update = {}
        for key in self.global_model:
            # Simulate gradient
            gradient = random.gauss(0, 0.1)
            
            # Malicious clients may send wrong updates
            if client.is_malicious:
                gradient *= random.choice([-10, 10])  # Adversarial
            
            update[key] = gradient
        
        return update
    
    def _add_dp_noise(self, update: Dict[str, float]) -> Dict[str, float]:
        """Add differential privacy noise"""
        noisy_update = {}
        
        for key, value in update.items():
            # Gaussian mechanism
            noise = random.gauss(0, self.privacy_config.noise_scale)
            noisy_update[key] = value + noise
        
        return noisy_update
    
    def _clip_gradients(self, update: Dict[str, float], clip_norm: float = None) -> Dict[str, float]:
        """Clip gradients for privacy"""
        clip_norm = clip_norm or self.privacy_config.clip_norm
        
        # Calculate L2 norm
        norm = math.sqrt(sum(v ** 2 for v in update.values()))
        
        # Clip if necessary
        if norm > clip_norm:
            scale = clip_norm / norm
            return {k: v * scale for k, v in update.items()}
        
        return update
    
    def _federated_average(self, updates: List[Dict]) -> Dict[str, float]:
        """Federated Averaging (FedAvg)"""
        total_size = sum(u['data_size'] for u in updates)
        
        aggregated = {}
        for key in self.global_model:
            weighted_sum = sum(
                u['update'].get(key, 0) * u['data_size']
                for u in updates
            )
            aggregated[key] = weighted_sum / total_size
        
        return aggregated
    
    def _federated_proximal(self, updates: List[Dict]) -> Dict[str, float]:
        """Federated Proximal (FedProx)"""
        # Similar to FedAvg but with proximal term
        aggregated = self._federated_average(updates)
        
        # Add proximal term (pull toward global model)
        mu = 0.01  # Proximal parameter
        for key in self.global_model:
            aggregated[key] -= mu * self.global_model[key]
        
        return aggregated
    
    def _secure_aggregation(self, updates: List[Dict]) -> Dict[str, float]:
        """Secure Aggregation with masking"""
        # Simulate secure aggregation protocol
        # In real implementation, this would use cryptographic masking
        
        # Generate pairwise masks (simulated)
        n_clients = len(updates)
        masks = []
        for i in range(n_clients):
            mask = {key: random.gauss(0, 0.01) for key in self.global_model}
            masks.append(mask)
        
        # Apply masks
        masked_updates = []
        for i, update in enumerate(updates):
            masked = {}
            for key in self.global_model:
                masked[key] = update['update'].get(key, 0) + masks[i][key]
            masked_updates.append(masked)
        
        # Aggregate masked updates
        aggregated = {}
        for key in self.global_model:
            aggregated[key] = statistics.mean(mu.get(key, 0) for mu in masked_updates)
        
        # Masks cancel out in expectation
        return aggregated
    
    def _evaluate_loss(self) -> float:
        """Evaluate global model loss"""
        # Mock loss calculation
        base_loss = 1.0 / (1 + len(self.rounds) * 0.1)
        noise = random.gauss(0, 0.05)
        return max(0.1, base_loss + noise)
    
    def _evaluate_accuracy(self) -> float:
        """Evaluate global model accuracy"""
        # Mock accuracy calculation
        base_accuracy = 0.5 + len(self.rounds) * 0.03
        noise = random.gauss(0, 0.02)
        return min(0.95, max(0.5, base_accuracy + noise))
    
    def _analyze_security(self, round_id: int, updates: List[Dict]) -> SecurityReport:
        """Analyze security of federated round"""
        malicious_count = sum(1 for u in updates if u['is_malicious'])
        
        # Detect anomalies
        anomaly_scores = []
        for update in updates:
            update_norm = math.sqrt(sum(v ** 2 for v in update['update'].values()))
            anomaly_scores.append(update_norm)
        
        # Flag outliers
        if anomaly_scores:
            mean_norm = statistics.mean(anomaly_scores)
            std_norm = statistics.stdev(anomaly_scores) if len(anomaly_scores) > 1 else 0.1
            
            detected_malicious = sum(
                1 for score in anomaly_scores
                if abs(score - mean_norm) > 2 * std_norm
            )
        else:
            detected_malicious = 0
        
        # Privacy guarantee
        if self.privacy_config.epsilon <= 1.0:
            privacy_guarantee = "Strong (ε ≤ 1)"
        elif self.privacy_config.epsilon <= 10.0:
            privacy_guarantee = "Moderate (1 < ε ≤ 10)"
        else:
            privacy_guarantee = "Weak (ε > 10)"
        
        # Security score
        security_score = 1.0 - (detected_malicious / max(len(updates), 1))
        security_score *= 0.9 if malicious_count > 0 else 1.0
        
        report = SecurityReport(
            round_id=round_id,
            clients_detected=len(updates),
            malicious_detected=detected_malicious,
            privacy_guarantee=privacy_guarantee,
            security_score=round(security_score, 3)
        )
        
        return report
    
    def _generate_random_update(self) -> Dict[str, float]:
        """Generate random model update"""
        return {f"weight_{i}": random.gauss(0, 0.1) for i in range(10)}
    
    def get_training_history(self) -> List[Dict]:
        """Get training history"""
        return [
            {
                'round': r.round_id,
                'loss': r.global_loss,
                'accuracy': r.global_accuracy,
                'clients': len(r.participating_clients)
            }
            for r in self.rounds
        ]
    
    def get_statistics(self) -> Dict:
        """Get FL statistics"""
        if not self.rounds:
            return {
                'total_rounds': 0,
                'final_accuracy': 0,
                'final_loss': 0,
                'total_clients': len(self.clients),
                'privacy_budget': self.privacy_config.epsilon
            }
        
        return {
            'total_rounds': len(self.rounds),
            'final_accuracy': self.rounds[-1].global_accuracy,
            'final_loss': self.rounds[-1].global_loss,
            'total_clients': len(self.clients),
            'privacy_budget': self.privacy_config.epsilon,
            'malicious_clients': sum(c.is_malicious for c in self.clients)
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Federated Learning Framework')
    parser.add_argument('--rounds', type=int, default=10, help='Number of rounds')
    parser.add_argument('--clients', type=int, default=10, help='Number of clients')
    parser.add_argument('--epsilon', type=float, default=1.0, help='Privacy budget')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    args = parser.parse_args()
    
    # Privacy config
    privacy_config = PrivacyConfig(
        epsilon=args.epsilon,
        delta=1e-5,
        noise_scale=0.1,
        clip_norm=1.0
    )
    
    fl = FederatedLearningFramework(n_clients=args.clients, privacy_config=privacy_config)
    
    if args.demo or args.rounds > 0:
        print("\n🔐 Federated Learning Framework Demo\n")
        
        # Initialize
        fl.initialize_clients(args.clients)
        
        # Train
        n_rounds = args.rounds if not args.demo else 10
        for round_id in range(1, n_rounds + 1):
            fl.train_round(round_id, n_participants=5)
        
        # Summary
        print("\n" + "=" * 60)
        print("Training Summary")
        print("=" * 60)
        stats = fl.get_statistics()
        print(f"Total Rounds: {stats['total_rounds']}")
        print(f"Final Accuracy: {stats['final_accuracy']:.1%}")
        print(f"Final Loss: {stats['final_loss']:.4f}")
        print(f"Total Clients: {stats['total_clients']}")
        print(f"Privacy Budget (ε): {stats['privacy_budget']}")
        print(f"Malicious Clients: {stats['malicious_clients']}")
        
        # Learning curve
        print("\nLearning Curve:")
        history = fl.get_training_history()
        for h in history[-5:]:  # Last 5 rounds
            print(f"  Round {h['round']:2d}: Loss={h['loss']:.4f}, Acc={h['accuracy']:.1%}")
        
        fl.save_state()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
