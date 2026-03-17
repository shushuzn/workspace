#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canvas Auto-Updater - Automatic knowledge graph updates

Features:
- Auto-update lessons canvas from MEMORY.md
- Auto-update workflows canvas from workflow files
- Scheduled updates via HEARTBEAT
- Change detection (only update if changed)
- UTF-8 encoding support

Author: OpenClaw Team
Date: 2026-03-16
Version: 1.0
"""

import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# UTF-8 encoding for Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

# Import Canvas generator
sys.path.insert(0, str(Path(__file__).parent))
try:
    from json_canvas_generator import JsonCanvasGenerator
    CANVAS_AVAILABLE = True
except ImportError:
    CANVAS_AVAILABLE = False
    print("⚠️  Canvas generator not found")


class CanvasAutoUpdater:
    """Automatic canvas file updater"""
    
    def __init__(self, workspace_dir: Optional[str] = None):
        if workspace_dir:
            self.workspace = Path(workspace_dir)
        else:
            self.workspace = Path(__file__).parent.parent
        
        self.config_dir = self.workspace / "00-config"
        self.memory_file = self.workspace / "MEMORY.md"
        self.workflows_dir = self.workspace / "30-scripts-tools"
        self.state_file = self.config_dir / "canvas_state.json"
        
        self.generator = JsonCanvasGenerator() if CANVAS_AVAILABLE else None
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load updater state"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            'lessons': {
                'last_hash': None,
                'last_update': None,
                'update_count': 0
            },
            'workflows': {
                'last_hash': None,
                'last_update': None,
                'update_count': 0
            }
        }
    
    def _save_state(self):
        """Save updater state"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def _get_file_hash(self, filepath: Path) -> Optional[str]:
        """Calculate file hash for change detection"""
        if not filepath.exists():
            return None
        
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _needs_update(self, key: str, filepath: Path) -> bool:
        """Check if canvas needs update"""
        current_hash = self._get_file_hash(filepath)
        
        if current_hash is None:
            return False
        
        last_hash = self.state.get(key, {}).get('last_hash')
        return current_hash != last_hash
    
    def update_lessons_canvas(self, force: bool = False) -> Dict:
        """Update lessons canvas if MEMORY.md changed"""
        result = {
            'updated': False,
            'reason': None,
            'nodes': 0,
            'edges': 0,
            'file': None
        }
        
        if not self.generator:
            result['reason'] = 'Canvas generator not available'
            return result
        
        if not self.memory_file.exists():
            result['reason'] = 'MEMORY.md not found'
            return result
        
        # Check if update needed
        if not force and not self._needs_update('lessons', self.memory_file):
            result['reason'] = 'No changes detected'
            return result
        
        # Generate canvas
        output_file = self.config_dir / "lessons.canvas"
        
        try:
            self.generator.create_lessons_canvas(str(self.memory_file), str(output_file))
            
            # Update state
            self.state['lessons'] = {
                'last_hash': self._get_file_hash(self.memory_file),
                'last_update': datetime.now().isoformat(),
                'update_count': self.state['lessons'].get('update_count', 0) + 1
            }
            self._save_state()
            
            # Get stats
            with open(output_file, 'r', encoding='utf-8') as f:
                canvas_data = json.load(f)
            
            result['updated'] = True
            result['reason'] = 'Updated successfully'
            result['nodes'] = len(canvas_data.get('nodes', []))
            result['edges'] = len(canvas_data.get('edges', []))
            result['file'] = str(output_file)
            
        except Exception as e:
            result['reason'] = f'Error: {str(e)}'
        
        return result
    
    def update_workflows_canvas(self, force: bool = False) -> Dict:
        """Update workflows canvas from workflow files"""
        result = {
            'updated': False,
            'reason': None,
            'nodes': 0,
            'edges': 0,
            'file': None
        }
        
        if not self.generator:
            result['reason'] = 'Canvas generator not available'
            return result
        
        # Scan for workflow files
        workflow_files = list(self.workflows_dir.glob("*workflow*.py"))
        workflow_files.extend(list(self.workflows_dir.glob("*engine*.py")))
        
        if not workflow_files:
            result['reason'] = 'No workflow files found'
            return result
        
        # Calculate combined hash
        combined_hash = hashlib.md5()
        for wf_file in workflow_files:
            if wf_file.exists():
                with open(wf_file, 'rb') as f:
                    combined_hash.update(f.read())
        
        # Check if update needed
        if not force:
            last_hash = self.state.get('workflows', {}).get('last_hash')
            if combined_hash.hexdigest() == last_hash:
                result['reason'] = 'No changes detected'
                return result
        
        # Generate sample workflows
        workflows = []
        for wf_file in workflow_files[:5]:  # Limit to 5
            workflow_name = wf_file.stem.replace('_', ' ').title()
            workflows.append({
                'name': workflow_name,
                'steps': ['Step 1', 'Step 2', 'Step 3']  # Placeholder
            })
        
        output_file = self.config_dir / "workflows.canvas"
        
        try:
            self.generator.create_workflow_canvas(workflows, str(output_file))
            
            # Update state
            self.state['workflows'] = {
                'last_hash': combined_hash.hexdigest(),
                'last_update': datetime.now().isoformat(),
                'update_count': self.state['workflows'].get('update_count', 0) + 1
            }
            self._save_state()
            
            # Get stats
            with open(output_file, 'r', encoding='utf-8') as f:
                canvas_data = json.load(f)
            
            result['updated'] = True
            result['reason'] = 'Updated successfully'
            result['nodes'] = len(canvas_data.get('nodes', []))
            result['edges'] = len(canvas_data.get('edges', []))
            result['file'] = str(output_file)
            
        except Exception as e:
            result['reason'] = f'Error: {str(e)}'
        
        return result
    
    def update_all(self, force: bool = False) -> Dict:
        """Update all canvases"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'lessons': self.update_lessons_canvas(force=force),
            'workflows': self.update_workflows_canvas(force=force),
            'summary': {
                'total_updated': 0,
                'total_nodes': 0,
                'total_edges': 0
            }
        }
        
        if results['lessons']['updated']:
            results['summary']['total_updated'] += 1
            results['summary']['total_nodes'] += results['lessons']['nodes']
            results['summary']['total_edges'] += results['lessons']['edges']
        
        if results['workflows']['updated']:
            results['summary']['total_updated'] += 1
            results['summary']['total_nodes'] += results['workflows']['nodes']
            results['summary']['total_edges'] += results['workflows']['edges']
        
        return results
    
    def get_status(self) -> Dict:
        """Get updater status"""
        return {
            'workspace': str(self.workspace),
            'memory_file': str(self.memory_file),
            'memory_exists': self.memory_file.exists(),
            'canvas_generator': '✅' if self.generator else '❌',
            'state': self.state,
            'last_lessons_update': self.state['lessons'].get('last_update'),
            'last_workflows_update': self.state['workflows'].get('last_update'),
            'total_lessons_updates': self.state['lessons'].get('update_count', 0),
            'total_workflows_updates': self.state['workflows'].get('update_count', 0)
        }


def demo():
    """Run auto-updater demo"""
    print("\n🎨 Canvas Auto-Updater Demo\n")
    
    updater = CanvasAutoUpdater()
    
    # Show status
    print("="*70)
    print("Status:")
    print("="*70)
    
    status = updater.get_status()
    for key, value in status.items():
        if not key.endswith('_exists') and not key.endswith('_update'):
            print(f"  {key}: {value}")
    
    print()
    
    # Force update
    print("="*70)
    print("Force Update:")
    print("="*70)
    
    results = updater.update_all(force=True)
    
    print()
    print(f"Lessons: {'✅' if results['lessons']['updated'] else '❌'} - {results['lessons']['reason']}")
    if results['lessons']['updated']:
        print(f"  Nodes: {results['lessons']['nodes']}, Edges: {results['lessons']['edges']}")
    
    print(f"Workflows: {'✅' if results['workflows']['updated'] else '❌'} - {results['workflows']['reason']}")
    if results['workflows']['updated']:
        print(f"  Nodes: {results['workflows']['nodes']}, Edges: {results['workflows']['edges']}")
    
    print()
    print(f"Total: {results['summary']['total_updated']} updated")
    print(f"       {results['summary']['total_nodes']} nodes, {results['summary']['total_edges']} edges")
    
    print()
    print("="*70)
    print("State:")
    print("="*70)
    
    print(f"  Lessons updates: {status['total_lessons_updates']}")
    print(f"  Workflows updates: {status['total_workflows_updates']}")


def heartbeat_handler():
    """HEARTBEAT integration handler"""
    print("\n🔄 HEARTBEAT: Canvas Auto-Update\n")
    
    updater = CanvasAutoUpdater()
    results = updater.update_all(force=False)
    
    if results['summary']['total_updated'] > 0:
        print(f"✅ Updated {results['summary']['total_updated']} canvas files")
        print(f"   {results['summary']['total_nodes']} nodes, {results['summary']['total_edges']} edges")
    else:
        print("ℹ️  No updates needed (no changes detected)")
    
    return results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Canvas Auto-Updater')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    parser.add_argument('--force', action='store_true', help='Force update')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--heartbeat', action='store_true', help='HEARTBEAT mode')
    args = parser.parse_args()
    
    if args.demo or (not args.status and not args.heartbeat):
        demo()
    elif args.status:
        updater = CanvasAutoUpdater()
        status = updater.get_status()
        print(json.dumps(status, indent=2))
    elif args.heartbeat:
        heartbeat_handler()
    else:
        updater = CanvasAutoUpdater()
        results = updater.update_all(force=args.force)
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
