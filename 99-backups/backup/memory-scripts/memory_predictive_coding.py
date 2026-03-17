"""
Memory Predictive Coding System
Phase 7: Predictive Coding Memory System

Core concept: Memory as active prediction, not passive storage
- Generative Model: Predict next memory state / user need
- Prediction Error: Difference between prediction and reality
- Model Update: Minimize future prediction error

Based on:
- Friston's Free Energy Principle
- Predictive Processing Theory (Clark, 2013)
- Hierarchical Predictive Coding (Rao & Ballard, 1999)
"""

import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
import numpy as np
from collections import defaultdict, deque

# Fix Windows UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class Prediction:
    """A prediction about future memory state or user need"""
    prediction_id: str
    timestamp: float
    prediction_type: str  # 'memory_access', 'user_need', 'system_state'
    predicted_content: Dict[str, Any]
    confidence: float  # 0.0 - 1.0
    time_horizon: float  # seconds into future
    hierarchical_level: int  # 1-5 (1=low-level, 5=high-level abstract)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Prediction':
        return cls(**data)


@dataclass
class PredictionError:
    """Error between prediction and actual outcome"""
    error_id: str
    prediction_id: str
    timestamp: float
    predicted_value: Any
    actual_value: Any
    error_magnitude: float  # Absolute difference
    error_type: str  # 'timing', 'content', 'confidence'
    surprise_level: float  # How surprising is this error?
    learning_signal: float  # Strength of learning signal
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class GenerativeModel:
    """Hierarchical generative model for prediction"""
    model_id: str
    created_at: float
    last_updated: float
    hierarchical_levels: int
    layer_weights: List[float]  # Weight for each hierarchical level
    prediction_history: List[Dict] = field(default_factory=list)
    error_history: List[Dict] = field(default_factory=list)
    accuracy_by_level: Dict[int, List[float]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)


class PredictiveCodingEngine:
    """
    Main predictive coding engine for memory system
    
    Architecture:
    1. Top-down: Generate predictions from generative model
    2. Bottom-up: Send prediction errors up the hierarchy
    3. Update: Minimize prediction error by updating model
    """
    
    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path)
        self.data_dir = self.workspace / "data" / "predictive_coding"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize generative model
        self.model = self._initialize_model()
        
        # Prediction queues
        self.active_predictions: Dict[str, Prediction] = {}
        self.prediction_queue: deque = deque(maxlen=1000)
        
        # Error tracking
        self.errors: List[PredictionError] = []
        self.error_by_type: Dict[str, List[PredictionError]] = defaultdict(list)
        
        # Statistics
        self.stats = {
            'total_predictions': 0,
            'total_errors': 0,
            'accuracy_overall': 0.0,
            'accuracy_by_level': {},
            'average_surprise': 0.0,
            'model_updates': 0
        }
        
        # Load existing state
        self._load_state()
    
    def _initialize_model(self) -> GenerativeModel:
        """Initialize hierarchical generative model"""
        return GenerativeModel(
            model_id="predictive_model_v1",
            created_at=time.time(),
            last_updated=time.time(),
            hierarchical_levels=5,
            layer_weights=[0.3, 0.25, 0.2, 0.15, 0.1],  # Lower levels have more weight
            accuracy_by_level={i: [] for i in range(1, 6)}
        )
    
    def _generate_prediction_id(self) -> str:
        """Generate unique prediction ID"""
        timestamp = str(time.time())
        content = f"pred_{timestamp}_{np.random.rand()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID"""
        timestamp = str(time.time())
        content = f"error_{timestamp}_{np.random.rand()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def predict(self, 
                prediction_type: str,
                context: Dict[str, Any],
                time_horizon: float = 300.0,  # 5 minutes default
                hierarchical_level: int = 3) -> Prediction:
        """
        Generate a prediction using the generative model
        
        Args:
            prediction_type: Type of prediction ('memory_access', 'user_need', 'system_state')
            context: Current context for prediction
            time_horizon: How far into future to predict (seconds)
            hierarchical_level: Level in hierarchy (1-5)
        
        Returns:
            Prediction object
        """
        # Get level-appropriate weights
        level_weight = self.model.layer_weights[hierarchical_level - 1]
        
        # Generate prediction based on history and context
        predicted_content = self._generate_prediction_content(
            prediction_type, context, hierarchical_level
        )
        
        # Calculate confidence based on historical accuracy at this level
        historical_accuracy = self._get_historical_accuracy(hierarchical_level)
        confidence = historical_accuracy * level_weight
        
        prediction = Prediction(
            prediction_id=self._generate_prediction_id(),
            timestamp=time.time(),
            prediction_type=prediction_type,
            predicted_content=predicted_content,
            confidence=confidence,
            time_horizon=time_horizon,
            hierarchical_level=hierarchical_level
        )
        
        # Store active prediction
        self.active_predictions[prediction.prediction_id] = prediction
        self.prediction_queue.append(prediction.to_dict())
        self.stats['total_predictions'] += 1
        
        # Save state
        self._save_state()
        
        return prediction
    
    def _generate_prediction_content(self, 
                                     prediction_type: str,
                                     context: Dict[str, Any],
                                     level: int) -> Dict[str, Any]:
        """Generate prediction content based on type and context"""
        
        if prediction_type == 'memory_access':
            # Predict which memory will be accessed next
            recent_access = self._get_recent_memory_access()
            return {
                'predicted_memory': recent_access.get('next_likely', 'MEMORY.md'),
                'access_probability': 0.7,
                'temporal_pattern': 'morning_peak'
            }
        
        elif prediction_type == 'user_need':
            # Predict user's next need based on context
            hour = datetime.now().hour
            if 9 <= hour <= 11:
                need = 'task_planning'
            elif 14 <= hour <= 16:
                need = 'code_review'
            else:
                need = 'information_retrieval'
            
            return {
                'predicted_need': need,
                'confidence_by_time': 0.65,
                'context_match': context.get('activity', 'unknown')
            }
        
        elif prediction_type == 'system_state':
            # Predict system state changes
            return {
                'predicted_load': 'medium',
                'memory_usage_trend': 'stable',
                'recommended_action': 'none'
            }
        
        return {}
    
    def _get_recent_memory_access(self) -> Dict:
        """Get recent memory access patterns"""
        # In production, this would query actual access logs
        return {
            'last_accessed': 'MEMORY.md',
            'access_frequency': 5,
            'next_likely': 'HEARTBEAT.md'
        }
    
    def _get_historical_accuracy(self, level: int) -> float:
        """Get historical prediction accuracy for a hierarchical level"""
        if level in self.model.accuracy_by_level:
            accuracies = self.model.accuracy_by_level[level]
            if accuracies:
                return np.mean(accuracies[-100:])  # Last 100 predictions
        return 0.5  # Default prior
    
    def observe(self, 
                prediction_id: str, 
                actual_outcome: Any) -> PredictionError:
        """
        Observe actual outcome and compute prediction error
        
        Args:
            prediction_id: ID of the prediction to evaluate
            actual_outcome: What actually happened
        
        Returns:
            PredictionError object
        """
        if prediction_id not in self.active_predictions:
            raise ValueError(f"Prediction {prediction_id} not found")
        
        prediction = self.active_predictions[prediction_id]
        
        # Compute error magnitude
        error_magnitude, error_type = self._compute_error(
            prediction.predicted_content, actual_outcome
        )
        
        # Compute surprise level (how unexpected was this?)
        surprise_level = self._compute_surprise(
            prediction.confidence, error_magnitude
        )
        
        # Compute learning signal strength
        learning_signal = surprise_level * error_magnitude
        
        error = PredictionError(
            error_id=self._generate_error_id(),
            prediction_id=prediction_id,
            timestamp=time.time(),
            predicted_value=prediction.predicted_content,
            actual_value=actual_outcome,
            error_magnitude=error_magnitude,
            error_type=error_type,
            surprise_level=surprise_level,
            learning_signal=learning_signal
        )
        
        # Store error
        self.errors.append(error)
        self.error_by_type[error_type].append(error)
        self.stats['total_errors'] += 1
        
        # Update accuracy tracking
        accuracy = 1.0 - min(error_magnitude, 1.0)
        level = prediction.hierarchical_level
        self.model.accuracy_by_level[level].append(accuracy)
        
        # Keep only last 1000 accuracies per level
        if len(self.model.accuracy_by_level[level]) > 1000:
            self.model.accuracy_by_level[level] = self.model.accuracy_by_level[level][-1000:]
        
        # Update model if error is significant
        if learning_signal > 0.3:
            self._update_model(error)
        
        # Remove from active predictions
        del self.active_predictions[prediction_id]
        
        # Save state
        self._save_state()
        
        return error
    
    def _compute_error(self, predicted: Any, actual: Any) -> Tuple[float, str]:
        """Compute error magnitude and type"""
        if isinstance(predicted, dict) and isinstance(actual, dict):
            # Compare dictionaries
            common_keys = set(predicted.keys()) & set(actual.keys())
            if not common_keys:
                return 1.0, 'content'
            
            differences = sum(
                1 for k in common_keys 
                if str(predicted[k]) != str(actual[k])
            )
            error_magnitude = differences / len(common_keys)
            error_type = 'content'
        
        elif isinstance(predicted, (int, float)) and isinstance(actual, (int, float)):
            # Numeric comparison
            max_val = max(abs(predicted), abs(actual), 1e-10)
            error_magnitude = abs(predicted - actual) / max_val
            error_type = 'magnitude'
        
        else:
            # String or other comparison
            error_magnitude = 0.0 if str(predicted) == str(actual) else 1.0
            error_type = 'content'
        
        return error_magnitude, error_type
    
    def _compute_surprise(self, confidence: float, error_magnitude: float) -> float:
        """
        Compute surprise level
        
        Surprise is high when:
        - Confidence was high but error is large
        - Confidence was low but error is small (also surprising!)
        """
        # Expected error based on confidence
        expected_error = 1.0 - confidence
        
        # Surprise = |actual_error - expected_error|
        surprise = abs(error_magnitude - expected_error)
        
        return min(surprise, 1.0)  # Normalize to 0-1
    
    def _update_model(self, error: PredictionError):
        """Update generative model based on prediction error"""
        # Adjust layer weights based on error
        # Higher learning signal → larger update
        
        learning_rate = error.learning_signal * 0.1  # Max 10% adjustment
        
        # Update weights (simplified gradient descent)
        for i in range(len(self.model.layer_weights)):
            if error.learning_signal > 0.5:
                # Significant error → adjust weights
                self.model.layer_weights[i] *= (1.0 - learning_rate)
        
        # Normalize weights to sum to 1
        total = sum(self.model.layer_weights)
        self.model.layer_weights = [w / total for w in self.model.layer_weights]
        
        self.model.last_updated = time.time()
        self.stats['model_updates'] += 1
    
    def get_prediction_status(self) -> Dict:
        """Get current prediction status"""
        # Calculate overall accuracy
        if self.stats['total_predictions'] > 0:
            self.stats['accuracy_overall'] = 1.0 - (
                self.stats['total_errors'] / self.stats['total_predictions']
            )
        
        # Calculate average surprise
        if self.errors:
            self.stats['average_surprise'] = np.mean([e.surprise_level for e in self.errors])
        
        # Calculate accuracy by level
        self.stats['accuracy_by_level'] = {
            level: np.mean(accs) if accs else 0.0
            for level, accs in self.model.accuracy_by_level.items()
        }
        
        return {
            'active_predictions': len(self.active_predictions),
            'total_predictions': self.stats['total_predictions'],
            'total_errors': self.stats['total_errors'],
            'accuracy_overall': self.stats['accuracy_overall'],
            'accuracy_by_level': self.stats['accuracy_by_level'],
            'average_surprise': self.stats['average_surprise'],
            'model_updates': self.stats['model_updates'],
            'model_last_updated': self.model.last_updated
        }
    
    def _save_state(self):
        """Save engine state to disk"""
        state = {
            'model': self.model.to_dict(),
            'stats': self.stats,
            'recent_predictions': list(self.prediction_queue)[-100:],
            'recent_errors': [e.to_dict() for e in self.errors[-100:]]
        }
        
        state_file = self.data_dir / 'engine_state.json'
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def _load_state(self):
        """Load engine state from disk"""
        state_file = self.data_dir / 'engine_state.json'
        if not state_file.exists():
            return
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # Restore model
            model_data = state['model']
            self.model = GenerativeModel(
                model_id=model_data['model_id'],
                created_at=model_data['created_at'],
                last_updated=model_data['last_updated'],
                hierarchical_levels=model_data['hierarchical_levels'],
                layer_weights=model_data['layer_weights'],
                accuracy_by_level={
                    int(k): v for k, v in model_data['accuracy_by_level'].items()
                }
            )
            
            # Restore stats
            self.stats = state['stats']
            
        except Exception as e:
            print(f"⚠️ Could not load state: {e}")
    
    def run_autonomous_cycle(self, duration_seconds: int = 60) -> Dict:
        """
        Run autonomous prediction-observation cycle
        
        Simulates real-world usage for testing
        """
        print(f"🔮 Starting predictive coding cycle ({duration_seconds}s)...")
        
        start_time = time.time()
        predictions_made = 0
        errors_computed = 0
        
        while time.time() - start_time < duration_seconds:
            # Make prediction
            pred_type = np.random.choice(['memory_access', 'user_need', 'system_state'])
            prediction = self.predict(
                prediction_type=pred_type,
                context={'activity': 'autonomous_test'},
                time_horizon=5.0,
                hierarchical_level=np.random.randint(1, 6)
            )
            predictions_made += 1
            
            # Wait a bit
            time.sleep(0.5)
            
            # Simulate observation (in production, this would be real data)
            actual_outcome = self._simulate_outcome(prediction)
            error = self.observe(prediction.prediction_id, actual_outcome)
            errors_computed += 1
            
            # Log significant errors
            if error.surprise_level > 0.7:
                print(f"  ⚠️ High surprise: {error.error_type} (surprise={error.surprise_level:.2f})")
        
        # Return summary
        status = self.get_prediction_status()
        status['cycle_predictions'] = predictions_made
        status['cycle_errors'] = errors_computed
        
        print(f"✅ Cycle complete: {predictions_made} predictions, {errors_computed} errors")
        print(f"   Accuracy: {status['accuracy_overall']:.1%}")
        
        return status
    
    def _simulate_outcome(self, prediction: Prediction) -> Dict:
        """Simulate actual outcome for testing"""
        # Add some noise to make it realistic
        base_outcome = prediction.predicted_content.copy()
        
        # 70% chance of accurate prediction
        if np.random.rand() < 0.7:
            return base_outcome
        
        # 30% chance of error
        if 'predicted_memory' in base_outcome:
            base_outcome['predicted_memory'] = 'DIFFERENT_FILE.md'
        elif 'predicted_need' in base_outcome:
            base_outcome['predicted_need'] = 'different_need'
        
        return base_outcome


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Predictive Coding Engine')
    parser.add_argument('--workspace', type=str, default='.', 
                        help='Workspace path')
    parser.add_argument('--status', action='store_true',
                        help='Show current status')
    parser.add_argument('--run', type=int, default=0,
                        help='Run autonomous cycle for N seconds')
    parser.add_argument('--predict', type=str, choices=['memory_access', 'user_need', 'system_state'],
                        help='Make a prediction')
    
    args = parser.parse_args()
    
    # Initialize engine
    engine = PredictiveCodingEngine(args.workspace)
    
    if args.status:
        status = engine.get_prediction_status()
        print(json.dumps(status, indent=2))
    
    elif args.run > 0:
        results = engine.run_autonomous_cycle(args.run)
        print("\n📊 Results:")
        print(json.dumps(results, indent=2))
    
    elif args.predict:
        prediction = engine.predict(
            prediction_type=args.predict,
            context={'activity': 'manual_request'}
        )
        print(f"\n🔮 Prediction made:")
        print(f"   ID: {prediction.prediction_id}")
        print(f"   Type: {prediction.prediction_type}")
        print(f"   Confidence: {prediction.confidence:.1%}")
        print(f"   Level: {prediction.hierarchical_level}")
        print(f"   Content: {prediction.predicted_content}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
