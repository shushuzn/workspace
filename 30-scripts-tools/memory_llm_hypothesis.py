#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory LLM Hypothesis Generator (P5-1)
======================================
LLM-powered hypothesis generation for memory evolution.

Uses Ollama (qwen2.5:1.5b) to:
- Analyze patterns semantically
- Generate creative hypotheses
- Cross-domain analogy discovery
- Natural language descriptions

Version: 5.1.0
Author: Claw 🐾
Date: 2026-03-17
"""

import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import re

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import requests
except ImportError:
    print("Installing required package: requests")
    os.system("pip install requests")
    import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OllamaClient:
    """Local Ollama LLM client."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5:1.5b"):
        self.base_url = base_url
        self.model = model
        self.timeout = 120  # seconds
        
    def check_health(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def generate(self, prompt: str, stream: bool = False) -> str:
        """Generate text from prompt."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 1024
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            if stream:
                result = []
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        if 'response' in data:
                            result.append(data['response'])
                return ''.join(result)
            else:
                data = response.json()
                return data.get('response', '')
                
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout ({self.timeout}s)")
            return ""
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return ""
    
    def list_models(self) -> List[str]:
        """List available models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            data = response.json()
            return [m['name'] for m in data.get('models', [])]
        except Exception:
            return []


class LLMHypothesisGenerator:
    """LLM-powered hypothesis generator."""
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path(__file__).parent.parent
        self.ollama = OllamaClient()
        self.state_file = self.workspace_dir / "data" / "llm_hypotheses.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load state
        self.state = self._load_state()
        
        # Innovation patterns for context
        self.innovation_patterns = self._load_innovation_patterns()
        
    def _load_state(self) -> Dict:
        """Load state from file."""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "hypotheses": [],
            "total_generated": 0,
            "total_deployed": 0,
            "last_generation": None,
            "model_used": "qwen2.5:1.5b"
        }
    
    def _save_state(self):
        """Save state to file."""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False, default=str)
    
    def _load_innovation_patterns(self) -> List[Dict]:
        """Load existing innovation patterns."""
        # This would normally load from memory system
        # For now, use hardcoded patterns from P4-4
        return [
            {"name": "Biological Inspiration", "examples": ["Immune System", "Neural Network"]},
            {"name": "Physics Analogy", "examples": ["Thermodynamics", "Quantum Mechanics", "Time Crystal"]},
            {"name": "Mathematical Structure", "examples": ["Topology", "Fractal Geometry", "Graph Theory"]},
            {"name": "Consciousness Theory", "examples": ["Global Workspace", "IIT", "HOT"]},
            {"name": "Integration Pattern", "examples": ["Orchestrator", "Dashboard", "HEARTBEAT"]},
            {"name": "Self-Improvement", "examples": ["Pattern Mining", "Gap Detection", "Hypothesis Generation"]}
        ]
    
    def check_ollama_available(self) -> bool:
        """Check if Ollama is available."""
        if self.ollama.check_health():
            models = self.ollama.list_models()
            logger.info(f"Ollama available with models: {models}")
            return True
        else:
            logger.warning("Ollama not available, falling back to template-based generation")
            return False
    
    def generate_hypothesis(self, gap: Dict, patterns: List[Dict], use_llm: bool = True) -> Dict:
        """Generate hypothesis for a gap."""
        
        if use_llm and self.check_ollama_available():
            return self._generate_with_llm(gap, patterns)
        else:
            return self._generate_template(gap, patterns)
    
    def _generate_with_llm(self, gap: Dict, patterns: List[Dict]) -> Dict:
        """Generate hypothesis using LLM."""
        
        prompt = f"""You are an AI research innovation assistant. Your task is to generate creative hypotheses for improving a memory evolution system.

## Current Context
The system has these innovation patterns:
{json.dumps(patterns, indent=2)}

## Identified Gap
{json.dumps(gap, indent=2)}

## Task
Generate a specific, actionable hypothesis to address this gap.

## Output Format (JSON only, no extra text)
{{
    "title": "Short descriptive title",
    "description": "Detailed explanation (2-3 sentences)",
    "predicted_impact": "0.0-1.0 score",
    "implementation_effort": "Low/Medium/High",
    "estimated_time": "X hours",
    "related_patterns": ["pattern1", "pattern2"],
    "confidence": "0.0-1.0 score",
    "priority": "P0/P1/P2/P3"
}}

Generate ONLY the JSON, no other text."""

        response = self.ollama.generate(prompt)
        
        # Parse JSON from response
        try:
            # Extract JSON from response (may have markdown formatting)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                hypothesis = json.loads(json_match.group())
            else:
                hypothesis = json.loads(response)
            
            # Add metadata
            hypothesis['id'] = f"HYP-LLM-{self.state['total_generated'] + 1:03d}"
            hypothesis['generated_at'] = datetime.now().isoformat()
            hypothesis['method'] = 'llm'
            hypothesis['model'] = self.ollama.model
            hypothesis['gap_id'] = gap.get('id', 'unknown')
            hypothesis['status'] = 'pending'
            
            self.state['total_generated'] += 1
            self.state['hypotheses'].append(hypothesis)
            self.state['last_generation'] = datetime.now().isoformat()
            self._save_state()
            
            logger.info(f"Generated LLM hypothesis: {hypothesis['title']}")
            return hypothesis
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            # Fall back to template
            return self._generate_template(gap, patterns)
    
    def _generate_template(self, gap: Dict, patterns: List[Dict]) -> Dict:
        """Generate hypothesis using template (fallback)."""
        
        gap_name = gap.get('name', 'Unknown Gap')
        
        # Template-based generation
        templates = [
            {
                "title": f"Enhanced {gap_name} Detection",
                "description": f"Improve detection accuracy for {gap_name} using advanced pattern matching",
                "predicted_impact": 0.3,
                "implementation_effort": "Medium",
                "estimated_time": "4 hours",
                "related_patterns": ["Integration Pattern"],
                "confidence": 0.7,
                "priority": "P2"
            },
            {
                "title": f"Automated {gap_name} Resolution",
                "description": f"Implement automatic resolution mechanism for {gap_name}",
                "predicted_impact": 0.5,
                "implementation_effort": "High",
                "estimated_time": "8 hours",
                "related_patterns": ["Self-Improvement", "Integration Pattern"],
                "confidence": 0.6,
                "priority": "P1"
            },
            {
                "title": f"Cross-Domain {gap_name} Solution",
                "description": f"Apply biological/physics analogies to solve {gap_name}",
                "predicted_impact": 0.7,
                "implementation_effort": "High",
                "estimated_time": "12 hours",
                "related_patterns": ["Biological Inspiration", "Physics Analogy"],
                "confidence": 0.5,
                "priority": "P0"
            }
        ]
        
        # Select best template
        hypothesis = templates[0].copy()
        hypothesis['id'] = f"HYP-TPL-{self.state['total_generated'] + 1:03d}"
        hypothesis['generated_at'] = datetime.now().isoformat()
        hypothesis['method'] = 'template'
        hypothesis['gap_id'] = gap.get('id', 'unknown')
        hypothesis['status'] = 'pending'
        
        self.state['total_generated'] += 1
        self.state['hypotheses'].append(hypothesis)
        self.state['last_generation'] = datetime.now().isoformat()
        self._save_state()
        
        logger.info(f"Generated template hypothesis: {hypothesis['title']}")
        return hypothesis
    
    def generate_batch(self, gaps: List[Dict], use_llm: bool = True) -> List[Dict]:
        """Generate hypotheses for multiple gaps."""
        hypotheses = []
        
        for gap in gaps:
            hyp = self.generate_hypothesis(gap, self.innovation_patterns, use_llm)
            hypotheses.append(hyp)
        
        return hypotheses
    
    def get_hypotheses(self, status: str = None) -> List[Dict]:
        """Get hypotheses, optionally filtered by status."""
        if status:
            return [h for h in self.state['hypotheses'] if h.get('status') == status]
        return self.state['hypotheses']
    
    def deploy_hypothesis(self, hypothesis_id: str) -> bool:
        """Mark hypothesis as deployed."""
        for hyp in self.state['hypotheses']:
            if hyp['id'] == hypothesis_id:
                hyp['status'] = 'deployed'
                hyp['deployed_at'] = datetime.now().isoformat()
                self.state['total_deployed'] += 1
                self._save_state()
                logger.info(f"Deployed hypothesis: {hypothesis_id}")
                return True
        return False
    
    def get_statistics(self) -> Dict:
        """Get generation statistics."""
        hypotheses = self.state['hypotheses']
        
        by_status = {}
        by_priority = {}
        by_method = {}
        
        for hyp in hypotheses:
            status = hyp.get('status', 'unknown')
            priority = hyp.get('priority', 'unknown')
            method = hyp.get('method', 'unknown')
            
            by_status[status] = by_status.get(status, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1
            by_method[method] = by_method.get(method, 0) + 1
        
        return {
            "total_generated": self.state['total_generated'],
            "total_deployed": self.state['total_deployed'],
            "by_status": by_status,
            "by_priority": by_priority,
            "by_method": by_method,
            "last_generation": self.state['last_generation'],
            "model_used": self.state['model_used']
        }
    
    def export_report(self, output_file: str = None) -> str:
        """Export generation report."""
        if not output_file:
            output_file = self.workspace_dir / "data" / f"llm_hypotheses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        else:
            output_file = Path(output_file)
        
        stats = self.get_statistics()
        hypotheses = self.state['hypotheses']
        
        report = f"""# LLM Hypothesis Generation Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Model:** {stats['model_used']}  
**Total Generated:** {stats['total_generated']}  
**Total Deployed:** {stats['total_deployed']}

## Statistics

### By Status
{json.dumps(stats['by_status'], indent=2)}

### By Priority
{json.dumps(stats['by_priority'], indent=2)}

### By Method
{json.dumps(stats['by_method'], indent=2)}

## Generated Hypotheses

"""
        
        for hyp in hypotheses:
            report += f"""### {hyp['id']}: {hyp['title']}

- **Status:** {hyp['status']}
- **Priority:** {hyp['priority']}
- **Method:** {hyp['method']}
- **Predicted Impact:** {hyp['predicted_impact']}
- **Confidence:** {hyp['confidence']}
- **Effort:** {hyp['implementation_effort']}
- **Time:** {hyp['estimated_time']}
- **Description:** {hyp['description']}
- **Related Patterns:** {', '.join(hyp['related_patterns'])}

---

"""
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Report exported to: {output_file}")
        return str(output_file)


def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="LLM Hypothesis Generator (P5-1)")
    parser.add_argument("--check", action="store_true", help="Check Ollama availability")
    parser.add_argument("--generate", action="store_true", help="Generate hypotheses for current gaps")
    parser.add_argument("--batch", type=int, help="Generate batch of N hypotheses")
    parser.add_argument("--list", action="store_true", help="List all hypotheses")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--deploy", type=str, help="Deploy hypothesis by ID")
    parser.add_argument("--export", action="store_true", help="Export report")
    parser.add_argument("--force-llm", action="store_true", help="Force LLM mode (fail if unavailable)")
    parser.add_argument("--workspace", type=str, default=None, help="Workspace directory")
    
    args = parser.parse_args()
    
    generator = LLMHypothesisGenerator(args.workspace)
    
    if args.check:
        available = generator.check_ollama_available()
        print(f"Ollama available: {available}")
        if available:
            models = generator.ollama.list_models()
            print(f"Available models: {models}")
        return 0 if available else 1
    
    elif args.generate:
        # Demo gaps
        demo_gaps = [
            {"id": "GAP-001", "name": "Pattern Diversity", "description": "Limited pattern variety"},
            {"id": "GAP-002", "name": "Hypothesis Quality", "description": "Low confidence scores"},
            {"id": "GAP-003", "name": "Deployment Speed", "description": "Slow deployment cycle"}
        ]
        
        use_llm = not args.force_llm  # Use LLM if available, fallback otherwise
        if args.force_llm and not generator.check_ollama_available():
            print("Error: Ollama not available and --force-llm specified")
            return 1
        
        hypotheses = generator.generate_batch(demo_gaps, use_llm=use_llm)
        
        print(f"\nGenerated {len(hypotheses)} hypotheses:\n")
        for hyp in hypotheses:
            print(f"{hyp['id']}: {hyp['title']} (Priority: {hyp['priority']}, Impact: {hyp['predicted_impact']})")
        
        return 0
    
    elif args.list:
        hypotheses = generator.get_hypotheses()
        if not hypotheses:
            print("No hypotheses generated yet")
            return 0
        
        print(f"\nTotal: {len(hypotheses)} hypotheses\n")
        for hyp in hypotheses:
            print(f"{hyp['id']}: {hyp['title']}")
            print(f"  Status: {hyp['status']}, Priority: {hyp['priority']}")
            print(f"  Method: {hyp['method']}, Impact: {hyp['predicted_impact']}")
            print()
        
        return 0
    
    elif args.stats:
        stats = generator.get_statistics()
        print("\n=== LLM Hypothesis Generation Statistics ===\n")
        print(f"Total Generated: {stats['total_generated']}")
        print(f"Total Deployed: {stats['total_deployed']}")
        print(f"Model Used: {stats['model_used']}")
        print(f"Last Generation: {stats['last_generation']}")
        print(f"\nBy Status: {stats['by_status']}")
        print(f"By Priority: {stats['by_priority']}")
        print(f"By Method: {stats['by_method']}")
        return 0
    
    elif args.deploy:
        success = generator.deploy_hypothesis(args.deploy)
        if success:
            print(f"Deployed: {args.deploy}")
            return 0
        else:
            print(f"Failed to deploy: {args.deploy}")
            return 1
    
    elif args.export:
        report_path = generator.export_report()
        print(f"Report exported to: {report_path}")
        return 0
    
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
