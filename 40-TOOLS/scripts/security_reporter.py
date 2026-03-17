#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security Reporter - Generate comprehensive security reports
Part of Security Audit Automation System (BRAIN-011)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class SecurityReporter:
    """Generate comprehensive security reports"""
    
    def __init__(self, report_dir: str = "data"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(exist_ok=True)
        
    def load_scan_results(self, scan_file: str) -> Dict[str, Any]:
        """Load scan results from JSON file"""
        with open(scan_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def calculate_stats(self, data: Dict[str, Any]) -> Dict[str, int]:
        """Calculate vulnerability statistics"""
        stats = {
            'total': 0,
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'files_affected': set(),
            'types': {}
        }
        
        # Handle different formats
        issues = data.get('issues', []) or data.get('findings', [])
        if not issues:
            # Try old format
            for file_path, vulns in data.get('files', {}).items():
                stats['files_affected'].add(file_path)
                for vuln in vulns:
                    self._process_vuln(vuln, stats)
        else:
            # New format: issues/findings list
            for issue in issues:
                self._process_vuln(issue, stats)
        
        stats['files_affected'] = len(stats['files_affected'])
        return stats
    
    def _process_vuln(self, vuln: Dict, stats: Dict[str, int]):
        """Process a single vulnerability"""
        stats['total'] += 1
        stats['files_affected'].add(vuln.get('file', 'unknown'))
        
        severity = vuln.get('severity', 'MEDIUM').upper()
        if severity == 'CRITICAL':
            stats['critical'] += 1
        elif severity == 'HIGH':
            stats['high'] += 1
        elif severity == 'MEDIUM':
            stats['medium'] += 1
        else:
            stats['low'] += 1
        
        vuln_type = vuln.get('type', 'UNKNOWN')
        stats['types'][vuln_type] = stats['types'].get(vuln_type, 0) + 1
    
    def generate_markdown_report(self, data: Dict[str, Any]) -> str:
        """Generate comprehensive markdown report"""
        stats = self.calculate_stats(data)
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        output_file = self.report_dir / f"security_report_{timestamp}.md"
        
        risk_level = "CRITICAL" if stats['critical'] > 100 else "HIGH" if stats['critical'] > 10 else "MEDIUM"
        
        # Calculate percentages safely
        def safe_pct(num, denom):
            return f"{num/denom*100:.1f}%" if denom > 0 else "0%"
        
        report = f"""# Security Audit Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

**Risk Level:** {risk_level}  
**Total Files Scanned:** {stats['files_affected']}  
**Total Vulnerabilities:** {stats['total']:,}

### Severity Breakdown
- 🔴 **CRITICAL:** {stats['critical']:,} ({safe_pct(stats['critical'], stats['total'])})
- 🟠 **HIGH:** {stats['high']:,} ({safe_pct(stats['high'], stats['total'])})
- 🟡 **MEDIUM:** {stats['medium']:,} ({safe_pct(stats['medium'], stats['total'])})
- 🟢 **LOW:** {stats['low']:,} ({safe_pct(stats['low'], stats['total'])})

### Top Vulnerability Types
"""
        
        sorted_types = sorted(stats['types'].items(), key=lambda x: x[1], reverse=True)[:5]
        for i, (vuln_type, count) in enumerate(sorted_types, 1):
            report += f"{i}. **{vuln_type}:** {count:,} occurrences\n"
        
        report += "\n## Remediation Priority\n\n"
        report += "### CRITICAL (Immediate Action)\n\n"
        report += "1. **HARDCODED_SECRET** - Rotate all exposed secrets\n"
        report += "2. **SQL_INJECTION** - Fix parameterized queries\n\n"
        report += "### HIGH (24-48 Hours)\n\n"
        report += "1. **MISSING_INPUT_VALIDATION** - Add pydantic validation\n"
        report += "2. **WEAK_CRYPTOGRAPHY** - Upgrade to SHA-256/AES-256\n\n"
        
        report += "## Next Steps\n\n"
        report += "1. Rotate all exposed secrets immediately\n"
        report += "2. Create .env file for secret management\n"
        report += "3. Add .env to .gitignore\n"
        report += "4. Run automated remediation script\n"
        report += "5. Schedule weekly security scans\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Report saved to: {output_file}")
        return report
    
    def run_full_report(self, scan_file: str = "data/vulnerability_report.json"):
        """Run full security report generation"""
        print("=" * 80)
        print("Security Reporter - Generating Comprehensive Report")
        print("=" * 80)
        
        print(f"\nLoading scan results from: {scan_file}")
        data = self.load_scan_results(scan_file)
        
        print("\nGenerating markdown report...")
        self.generate_markdown_report(data)
        
        stats = self.calculate_stats(data)
        print("\n" + "=" * 80)
        print("Report Generation Complete!")
        print("=" * 80)
        print(f"Total Vulnerabilities: {stats['total']:,}")
        print(f"Files Affected: {stats['files_affected']:,}")
        print(f"Critical: {stats['critical']:,} | High: {stats['high']:,} | Medium: {stats['medium']:,}")
        print("=" * 80)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Security Reporter")
    parser.add_argument("--scan", type=str, default="data/vulnerability_report.json",
                       help="Scan results JSON file")
    parser.add_argument("--report", action="store_true",
                       help="Generate full report")
    
    args = parser.parse_args()
    
    reporter = SecurityReporter()
    
    if args.report:
        reporter.run_full_report(args.scan)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
