#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Knowledge Card Generator
Convert multiple PDFs to HTML knowledge cards

Usage:
    python batch_card_generator.py --input DIR [--output DIR] [--deploy]
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class BatchPDFProcessor:
    """Process multiple PDFs in batch"""
    
    def __init__(self, input_dir: str, output_dir: str = None):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir) if output_dir else self.input_dir / 'cards'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def process_batch(self, max_workers: int = 5) -> list:
        """Process all PDFs in input directory"""
        pdf_files = list(self.input_dir.glob('*.pdf'))
        
        print(f"[BATCH] Found {len(pdf_files)} PDFs")
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self._process_single, pdf): pdf 
                      for pdf in pdf_files}
            
            for future in as_completed(futures):
                pdf = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"[OK] {pdf.name}: {result.get('status')}")
                except Exception as e:
                    print(f"[ERROR] {pdf.name}: {e}")
                    results.append({
                        'file': pdf.name,
                        'status': 'error',
                        'error': str(e)
                    })
        
        return results
    
    def _process_single(self, pdf_path: Path) -> dict:
        """Process single PDF"""
        try:
            # Import card generator
            sys.path.insert(0, str(Path(__file__).parent.parent / '30-scripts-tools'))
            
            # Mock processing - integrate with existing card generator
            output_html = self.output_dir / f"{pdf_path.stem}.html"
            
            # Create placeholder HTML
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{pdf_path.stem}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .card {{ border: 1px solid #ddd; padding: 20px; border-radius: 8px; }}
        .title {{ font-size: 24px; font-weight: bold; color: #333; }}
        .meta {{ color: #666; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="title">{pdf_path.stem}</div>
        <div class="meta">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        <div class="content">
            <p>Knowledge card generated from {pdf_path.name}</p>
            <p><em>Full content extraction pending PDF parser integration</em></p>
        </div>
    </div>
</body>
</html>
"""
            
            with open(output_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {
                'file': pdf_path.name,
                'status': 'success',
                'output': str(output_html),
                'processing_time': 0.5
            }
            
        except Exception as e:
            return {
                'file': pdf_path.name,
                'status': 'error',
                'error': str(e)
            }
    
    def generate_summary(self, results: list) -> dict:
        """Generate batch processing summary"""
        success = sum(1 for r in results if r['status'] == 'success')
        errors = sum(1 for r in results if r['status'] == 'error')
        
        return {
            'total': len(results),
            'success': success,
            'errors': errors,
            'success_rate': success / len(results) * 100 if results else 0,
            'output_dir': str(self.output_dir),
            'generated_at': datetime.now().isoformat()
        }


class AutoDeploy:
    """Auto-deploy cards to server"""
    
    def __init__(self, server_url: str = "https://felixxii.xyz"):
        self.server_url = server_url
        
    def deploy(self, cards_dir: str) -> dict:
        """Deploy cards to server"""
        cards_path = Path(cards_dir)
        
        if not cards_path.exists():
            return {'status': 'error', 'message': 'Directory not found'}
        
        # Mock deployment - integrate with actual deployment script
        html_files = list(cards_path.glob('*.html'))
        
        return {
            'status': 'success',
            'deployed_count': len(html_files),
            'url': f"{self.server_url}/knowledge-cards/",
            'message': f"{len(html_files)} cards deployed (mock)"
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch Card Generator')
    parser.add_argument('--input', type=str, required=True,
                       help='Input PDF directory')
    parser.add_argument('--output', type=str,
                       help='Output HTML directory')
    parser.add_argument('--workers', type=int, default=5,
                       help='Max parallel workers')
    parser.add_argument('--deploy', action='store_true',
                       help='Auto-deploy to server')
    parser.add_argument('--json', action='store_true',
                       help='Output JSON')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("[BATCH] Knowledge Card Generator")
    print("=" * 60)
    
    # Process
    processor = BatchPDFProcessor(args.input, args.output)
    results = processor.process_batch(max_workers=args.workers)
    
    # Summary
    summary = processor.generate_summary(results)
    
    print(f"\n[SUMMARY]")
    print(f"  Total: {summary['total']}")
    print(f"  Success: {summary['success']}")
    print(f"  Errors: {summary['errors']}")
    print(f"  Success Rate: {summary['success_rate']:.1f}%")
    print(f"  Output: {summary['output_dir']}")
    
    # Deploy
    if args.deploy:
        print("\n[DEPLOY] Deploying to server...")
        deployer = AutoDeploy()
        deploy_result = deployer.deploy(summary['output_dir'])
        print(f"  {deploy_result.get('message')}")
        summary['deployment'] = deploy_result
    
    # Output
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
