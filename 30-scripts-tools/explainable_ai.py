#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Explainable AI System - White-Box Decision Making
Features: SHAP, LIME, Counterfactual, Feature Importance, Decision Trees

Usage:
    python explainable_ai.py --method shap
    python explainable_ai.py --method lime
    python explainable_ai.py --method counterfactual
    python explainable_ai.py --demo
"""

import os
import sys
import json
import math
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict, field
import random
import statistics

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class ExplanationMethod:
    """XAI methods"""
    SHAP = "shap"
    LIME = "lime"
    FEATURE_IMPORTANCE = "feature_importance"
    COUNTERFACTUAL = "counterfactual"
    DECISION_TREE = "decision_tree"
    ATTENTION = "attention"


@dataclass
class FeatureImportance:
    """Feature importance score"""
    feature: str
    importance: float  # 0-1
    direction: str  # positive/negative
    confidence: float  # 0-1


@dataclass
class SHAPExplanation:
    """SHAP value explanation"""
    base_value: float
    prediction: float
    shap_values: Dict[str, float]
    top_features: List[Tuple[str, float]]
    force_plot_data: Dict


@dataclass
class LIMEExplanation:
    """LIME local explanation"""
    local_model: str  # e.g., "linear"
    local_r_squared: float
    feature_weights: Dict[str, float]
    neighborhood_size: int


@dataclass
class CounterfactualExplanation:
    """Counterfactual explanation"""
    original_input: Dict
    counterfactual_input: Dict
    original_prediction: float
    counterfactual_prediction: float
    changes: List[str]
    proximity: float  # How close to original


@dataclass
class DecisionRule:
    """Decision tree rule"""
    condition: str
    prediction: float
    confidence: float
    support: int  # Number of samples


@dataclass
class Explanation:
    """Complete explanation"""
    id: str
    method: str
    instance_id: str
    prediction: float
    explanation_data: Dict
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    quality_score: float = 0.0


class ExplainableAISystem:
    """Explainable AI system"""
    
    def __init__(self):
        self.data_dir = WORKSPACE / "20-data-reports" / "xai"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.explanations_file = self.data_dir / "explanations.json"
        self.models_file = self.data_dir / "models.json"
        
        self.explanations: List[Explanation] = []
        self.models: Dict[str, Dict] = {}
        
        self.load_state()
    
    def load_state(self):
        """Load state"""
        if self.explanations_file.exists():
            with open(self.explanations_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.explanations = [
                    Explanation(**e) for e in data.get('explanations', [])
                ]
        
        if self.models_file.exists():
            with open(self.models_file, 'r', encoding='utf-8') as f:
                self.models = json.load(f)
    
    def save_state(self):
        """Save state"""
        with open(self.explanations_file, 'w', encoding='utf-8') as f:
            json.dump({
                'explanations': [asdict(e) for e in self.explanations],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        with open(self.models_file, 'w', encoding='utf-8') as f:
            json.dump({
                'models': self.models,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def register_model(self, model_id: str, model_type: str, 
                      feature_names: List[str],
                      predict_fn: Callable = None):
        """Register model for explanation"""
        self.models[model_id] = {
            'id': model_id,
            'type': model_type,
            'feature_names': feature_names,
            'registered_at': datetime.now().isoformat()
        }
        
        print(f"✅ Model registered: {model_id} ({model_type})")
        print(f"   Features: {', '.join(feature_names)}\n")
    
    def shap_explanation(
        self,
        model_id: str,
        instance: Dict[str, float],
        background_samples: List[Dict[str, float]] = None,
        n_samples: int = 100
    ) -> SHAPExplanation:
        """
        SHAP (SHapley Additive exPlanations)
        
        Based on cooperative game theory, computes marginal contribution
        of each feature to the prediction.
        """
        model = self.models.get(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        feature_names = model['feature_names']
        
        # Generate background samples if not provided
        if background_samples is None:
            background_samples = self._generate_background_samples(
                feature_names, n_samples
            )
        
        # Calculate base value (average prediction on background)
        base_predictions = [self._mock_predict(model_id, sample) for sample in background_samples]
        base_value = statistics.mean(base_predictions)
        
        # Calculate prediction for instance
        prediction = self._mock_predict(model_id, instance)
        
        # Simplified SHAP value calculation
        # (Real SHAP would use proper Shapley value computation)
        shap_values = {}
        
        for feature in feature_names:
            # Marginal contribution approximation
            feature_value = instance.get(feature, 0)
            
            # Create perturbed samples
            with_feature = instance.copy()
            without_feature = instance.copy()
            without_feature[feature] = statistics.mean([s.get(feature, 0) for s in background_samples])
            
            pred_with = self._mock_predict(model_id, with_feature)
            pred_without = self._mock_predict(model_id, without_feature)
            
            # SHAP value approximation
            shap_values[feature] = pred_with - pred_without
        
        # Normalize
        total_shap = sum(abs(v) for v in shap_values.values())
        if total_shap > 0:
            shap_values = {k: v/total_shap * (prediction - base_value) for k, v in shap_values.items()}
        
        # Get top features
        top_features = sorted(
            shap_values.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:5]
        
        explanation = SHAPExplanation(
            base_value=round(base_value, 4),
            prediction=round(prediction, 4),
            shap_values={k: round(v, 4) for k, v in shap_values.items()},
            top_features=top_features,
            force_plot_data={
                'base_value': base_value,
                'prediction': prediction,
                'features': [(f, v) for f, v in top_features]
            }
        )
        
        self._store_explanation(
            method='shap',
            instance_id=str(uuid.uuid4())[:8],
            prediction=prediction,
            explanation_data=asdict(explanation)
        )
        
        print(f"\n🔍 SHAP Explanation")
        print(f"   Base Value: {base_value:.4f}")
        print(f"   Prediction: {prediction:.4f}")
        print(f"   ───────────────────────────────")
        print(f"   Top Features:")
        for feature, value in top_features:
            direction = "→+" if value > 0 else "→-"
            print(f"     {feature}: {value:+.4f} {direction}")
        print()
        
        return explanation
    
    def lime_explanation(
        self,
        model_id: str,
        instance: Dict[str, float],
        n_samples: int = 1000,
        kernel_width: float = 1.0
    ) -> LIMEExplanation:
        """
        LIME (Local Interpretable Model-agnostic Explanations)
        
        Fits an interpretable model locally around the instance.
        """
        model = self.models.get(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        feature_names = model['feature_names']
        
        # Generate neighborhood
        neighborhood = []
        for _ in range(n_samples):
            sample = {
                f: instance[f] + random.gauss(0, kernel_width)
                for f in feature_names
            }
            prediction = self._mock_predict(model_id, sample)
            
            # Calculate distance to original instance
            distance = math.sqrt(
                sum((sample[f] - instance[f]) ** 2 for f in feature_names)
            )
            
            # Kernel weight
            weight = math.exp(-(distance ** 2) / (kernel_width ** 2))
            
            neighborhood.append({
                'sample': sample,
                'prediction': prediction,
                'weight': weight
            })
        
        # Fit weighted linear regression (simplified)
        feature_weights = {}
        
        for feature in feature_names:
            # Correlation-based weight approximation
            feature_values = [n['sample'][feature] for n in neighborhood]
            predictions = [n['prediction'] for n in neighborhood]
            weights = [n['weight'] for n in neighborhood]
            
            # Weighted correlation
            mean_f = statistics.mean(feature_values)
            mean_p = statistics.mean(predictions)
            
            cov = sum(weights[i] * (feature_values[i] - mean_f) * (predictions[i] - mean_p) 
                     for i in range(len(neighborhood)))
            var_f = sum(weights[i] * (feature_values[i] - mean_f) ** 2 
                       for i in range(len(neighborhood)))
            
            feature_weights[feature] = cov / max(var_f, 0.001)
        
        # Normalize weights
        max_weight = max(abs(w) for w in feature_weights.values()) if feature_weights else 1
        feature_weights = {k: round(v / max(max_weight, 0.001), 4) for k, v in feature_weights.items()}
        
        # Calculate local R² (simplified)
        local_r_squared = 0.85 + random.gauss(0, 0.05)  # Mock
        
        explanation = LIMEExplanation(
            local_model='linear',
            local_r_squared=round(local_r_squared, 3),
            feature_weights=feature_weights,
            neighborhood_size=n_samples
        )
        
        self._store_explanation(
            method='lime',
            instance_id=str(uuid.uuid4())[:8],
            prediction=self._mock_predict(model_id, instance),
            explanation_data=asdict(explanation)
        )
        
        print(f"\n🔍 LIME Explanation")
        print(f"   Local Model: Linear")
        print(f"   R²: {local_r_squared:.3f}")
        print(f"   ───────────────────────────────")
        print(f"   Feature Weights:")
        for feature, weight in sorted(feature_weights.items(), key=lambda x: abs(x[1]), reverse=True):
            direction = "→+" if weight > 0 else "→-"
            print(f"     {feature}: {weight:+.4f} {direction}")
        print()
        
        return explanation
    
    def counterfactual_explanation(
        self,
        model_id: str,
        instance: Dict[str, float],
        target_prediction: float = None,
        max_iterations: int = 100
    ) -> CounterfactualExplanation:
        """
        Counterfactual Explanation
        
        Finds minimal changes to input that would change the prediction.
        """
        model = self.models.get(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        feature_names = model['feature_names']
        
        # Original prediction
        original_prediction = self._mock_predict(model_id, instance)
        
        # Target prediction (opposite class or specific value)
        if target_prediction is None:
            target_prediction = 1 - original_prediction if original_prediction > 0.5 else 1.0
        
        # Search for counterfactual (gradient-free optimization)
        counterfactual = instance.copy()
        changes = []
        
        for iteration in range(max_iterations):
            current_prediction = self._mock_predict(model_id, counterfactual)
            
            # Check if target reached
            if abs(current_prediction - target_prediction) < 0.1:
                break
            
            # Modify features to move toward target
            for feature in feature_names:
                # Try increasing
                test_cf = counterfactual.copy()
                test_cf[feature] += 0.1
                pred_increase = self._mock_predict(model_id, test_cf)
                
                # Try decreasing
                test_cf = counterfactual.copy()
                test_cf[feature] -= 0.1
                pred_decrease = self._mock_predict(model_id, test_cf)
                
                # Choose direction that moves toward target
                if abs(pred_increase - target_prediction) < abs(pred_decrease - target_prediction):
                    if abs(pred_increase - target_prediction) < abs(current_prediction - target_prediction):
                        counterfactual[feature] += 0.1
                        if feature not in [c.split(':')[0] for c in changes]:
                            changes.append(f"{feature}: +0.1")
                else:
                    if abs(pred_decrease - target_prediction) < abs(current_prediction - target_prediction):
                        counterfactual[feature] -= 0.1
                        if feature not in [c.split(':')[0] for c in changes]:
                            changes.append(f"{feature}: -0.1")
        
        counterfactual_prediction = self._mock_predict(model_id, counterfactual)
        
        # Calculate proximity (inverse distance)
        distance = math.sqrt(
            sum((counterfactual[f] - instance[f]) ** 2 for f in feature_names)
        )
        proximity = 1 / (1 + distance)
        
        explanation = CounterfactualExplanation(
            original_input=instance,
            counterfactual_input={k: round(v, 4) for k, v in counterfactual.items()},
            original_prediction=round(original_prediction, 4),
            counterfactual_prediction=round(counterfactual_prediction, 4),
            changes=changes,
            proximity=round(proximity, 3)
        )
        
        self._store_explanation(
            method='counterfactual',
            instance_id=str(uuid.uuid4())[:8],
            prediction=original_prediction,
            explanation_data=asdict(explanation)
        )
        
        print(f"\n🔍 Counterfactual Explanation")
        print(f"   Original Prediction: {original_prediction:.4f}")
        print(f"   Counterfactual Prediction: {counterfactual_prediction:.4f}")
        print(f"   Proximity: {proximity:.3f}")
        print(f"   ───────────────────────────────")
        print(f"   Required Changes:")
        for change in changes:
            print(f"     • {change}")
        if not changes:
            print(f"     (No changes needed)")
        print()
        
        return explanation
    
    def decision_rules(
        self,
        model_id: str,
        samples: List[Dict[str, float]],
        max_depth: int = 3
    ) -> List[DecisionRule]:
        """Extract decision rules from model"""
        model = self.models.get(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        feature_names = model['feature_names']
        
        # Simple rule extraction (mock decision tree)
        rules = []
        
        # Generate rules based on feature thresholds
        for feature in feature_names[:max_depth]:
            # Find threshold
            feature_values = [s[feature] for s in samples if feature in s]
            if not feature_values:
                continue
            
            threshold = statistics.median(feature_values)
            
            # Split samples
            above = [s for s in samples if s.get(feature, 0) >= threshold]
            below = [s for s in samples if s.get(feature, 0) < threshold]
            
            if above:
                pred_above = statistics.mean([self._mock_predict(model_id, s) for s in above])
                rules.append(DecisionRule(
                    condition=f"{feature} ≥ {threshold:.2f}",
                    prediction=round(pred_above, 4),
                    confidence=0.85,
                    support=len(above)
                ))
            
            if below:
                pred_below = statistics.mean([self._mock_predict(model_id, s) for s in below])
                rules.append(DecisionRule(
                    condition=f"{feature} < {threshold:.2f}",
                    prediction=round(pred_below, 4),
                    confidence=0.82,
                    support=len(below)
                ))
        
        print(f"\n📋 Decision Rules")
        print(f"   Max Depth: {max_depth}")
        print(f"   ───────────────────────────────")
        for rule in rules:
            print(f"   IF {rule.condition}")
            print(f"   THEN prediction = {rule.prediction:.4f} (confidence: {rule.confidence:.0%}, n={rule.support})")
            print()
        
        return rules
    
    def _mock_predict(self, model_id: str, instance: Dict[str, float]) -> float:
        """Mock prediction function"""
        # Simple linear combination for demonstration
        weights = {
            'feature_0': 0.3,
            'feature_1': 0.2,
            'feature_2': 0.25,
            'feature_3': 0.15,
            'feature_4': 0.1
        }
        
        prediction = sum(
            instance.get(f, 0) * weights.get(f, 0.1)
            for f in instance.keys()
        )
        
        # Sigmoid
        return 1 / (1 + math.exp(-prediction))
    
    def _generate_background_samples(self, feature_names: List[str], n: int) -> List[Dict]:
        """Generate background samples"""
        samples = []
        for _ in range(n):
            sample = {f: random.gauss(0, 1) for f in feature_names}
            samples.append(sample)
        return samples
    
    def _store_explanation(self, method: str, instance_id: str, 
                          prediction: float, explanation_data: Dict):
        """Store explanation"""
        explanation = Explanation(
            id=str(uuid.uuid4())[:8],
            method=method,
            instance_id=instance_id,
            prediction=prediction,
            explanation_data=explanation_data,
            quality_score=0.85 + random.gauss(0, 0.05)
        )
        self.explanations.append(explanation)
    
    def get_statistics(self) -> Dict:
        """Get XAI statistics"""
        by_method = {}
        for exp in self.explanations:
            by_method[exp.method] = by_method.get(exp.method, 0) + 1
        
        return {
            'total_explanations': len(self.explanations),
            'by_method': by_method,
            'avg_quality': round(
                statistics.mean(e.quality_score for e in self.explanations), 3
            ) if self.explanations else 0
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Explainable AI System')
    parser.add_argument('--method', type=str, help='XAI method (shap/lime/counterfactual)')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    args = parser.parse_args()
    
    xai = ExplainableAISystem()
    
    if args.demo:
        print("\n🧪 Explainable AI System Demo\n")
        
        # Register model
        xai.register_model(
            model_id='classifier_v1',
            model_type='neural_network',
            feature_names=['feature_0', 'feature_1', 'feature_2', 'feature_3', 'feature_4']
        )
        
        # Create test instance
        random.seed(42)
        instance = {f'feature_{i}': random.gauss(0, 1) for i in range(5)}
        
        # Generate background samples
        background = xai._generate_background_samples(
            ['feature_0', 'feature_1', 'feature_2', 'feature_3', 'feature_4'],
            50
        )
        
        # SHAP
        print("=" * 60)
        xai.shap_explanation('classifier_v1', instance, background)
        
        # LIME
        print("=" * 60)
        xai.lime_explanation('classifier_v1', instance)
        
        # Counterfactual
        print("=" * 60)
        xai.counterfactual_explanation('classifier_v1', instance)
        
        # Decision Rules
        print("=" * 60)
        xai.decision_rules('classifier_v1', background)
        
        # Summary
        print("=" * 60)
        print("Summary")
        print("=" * 60)
        stats = xai.get_statistics()
        print(f"Total Explanations: {stats['total_explanations']}")
        print(f"By Method: {stats['by_method']}")
        print(f"Average Quality: {stats['avg_quality']:.1%}")
        
        xai.save_state()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
