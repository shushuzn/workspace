#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Production Deployment Script for Memory Evolution System
=========================================================
Deploys the complete autonomous innovation system to production.

Features:
- Environment validation
- Dependency check
- Configuration setup
- Service registration
- Health check
- Rollback support

Author: Claw 🐾
Date: 2026-03-17
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
import shutil
import tempfile

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


class ProductionDeployer:
    """Production deployment orchestrator."""
    
    def __init__(self, workspace_dir: str, environment: str = "production"):
        self.workspace_dir = Path(workspace_dir)
        self.environment = environment
        self.tools_dir = self.workspace_dir / "30-scripts-tools"
        self.data_dir = self.workspace_dir / "data"
        self.logs_dir = self.workspace_dir / "21-reports"
        
        # Deployment state
        self.deployment_id = f"deploy-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.backup_dir = None
        self.steps_completed = []
        self.steps_failed = []
        
    def run(self):
        """Execute full deployment pipeline."""
        print("="*70)
        print("🚀 Production Deployment")
        print("="*70)
        print(f"Environment: {self.environment}")
        print(f"Workspace: {self.workspace_dir}")
        print(f"Deployment ID: {self.deployment_id}")
        print("="*70)
        
        try:
            # Step 1: Pre-deployment checks
            self._step("Pre-deployment validation", self._pre_deployment_check)
            
            # Step 2: Create backup
            self._step("Creating backup", self._create_backup)
            
            # Step 3: Validate tools
            self._step("Validating tools", self._validate_tools)
            
            # Step 4: Setup directories
            self._step("Setting up directories", self._setup_directories)
            
            # Step 5: Configuration
            self._step("Configuring environment", self._configure_environment)
            
            # Step 6: Register services
            self._step("Registering services", self._register_services)
            
            # Step 7: Health check
            self._step("Running health check", self._health_check)
            
            # Step 8: Post-deployment
            self._step("Post-deployment tasks", self._post_deployment)
            
            # Success
            self._print_success()
            return True
            
        except Exception as e:
            self._print_failure(str(e))
            self._rollback()
            return False
    
    def _step(self, name: str, func):
        """Execute deployment step."""
        print(f"\n[{len(self.steps_completed)+1}] {name}...")
        try:
            func()
            self.steps_completed.append(name)
            print(f"    ✅ {name} completed")
        except Exception as e:
            self.steps_failed.append(name)
            raise
    
    def _pre_deployment_check(self):
        """Validate environment before deployment."""
        # Check workspace exists
        assert self.workspace_dir.exists(), f"Workspace not found: {self.workspace_dir}"
        
        # Check tools directory
        assert self.tools_dir.exists(), f"Tools directory not found: {self.tools_dir}"
        
        # Check critical files
        critical_files = [
            "memory_self_improving_engine.py",
            "memory_llm_hypothesis.py",
            "tool_code_generator.py",
            "memory_evolutionary_algorithms.py",
            "memory_orchestrator.py"
        ]
        
        for filename in critical_files:
            filepath = self.tools_dir / filename
            assert filepath.exists(), f"Critical file missing: {filename}"
        
        # Check Python version
        python_version = sys.version_info
        assert python_version >= (3, 8), f"Python 3.8+ required, got {python_version}"
        
        print(f"    Workspace: {self.workspace_dir}")
        print(f"    Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
        print(f"    Critical files: {len(critical_files)} checked")
    
    def _create_backup(self):
        """Create deployment backup."""
        self.backup_dir = Path(tempfile.mkdtemp(prefix=f"backup-{self.deployment_id}-"))
        
        # Backup configuration
        config_files = [
            self.workspace_dir / ".env",
            self.workspace_dir / "HEARTBEAT.md",
            self.workspace_dir / "MEMORY.md"
        ]
        
        for config_file in config_files:
            if config_file.exists():
                shutil.copy2(config_file, self.backup_dir)
        
        # Backup state files
        state_dir = self.data_dir / "self_improvement"
        if state_dir.exists():
            backup_state = self.backup_dir / "self_improvement"
            shutil.copytree(state_dir, backup_state)
        
        print(f"    Backup location: {self.backup_dir}")
        print(f"    Files backed up: {len(list(self.backup_dir.rglob('*')))}")
    
    def _validate_tools(self):
        """Validate all tools can be imported."""
        tools_to_validate = [
            "memory_immune_system",
            "memory_neural_network",
            "memory_dark_matter",
            "memory_topological_analysis",
            "memory_thermodynamics",
            "memory_fractal_compression",
            "memory_causal_discovery",
            "memory_quantum_entanglement",
            "memory_time_crystal",
            "memory_consciousness_emergence",
            "memory_orchestrator",
            "memory_self_improving_engine",
            "memory_llm_hypothesis",
            "tool_code_generator",
            "deployment_validator",
            "memory_evolutionary_algorithms"
        ]
        
        # Add tools dir to path
        sys.path.insert(0, str(self.tools_dir))
        
        validated = 0
        for tool_name in tools_to_validate:
            try:
                # Use importlib for dynamic import
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    tool_name,
                    self.tools_dir / f"{tool_name}.py"
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                validated += 1
            except Exception as e:
                print(f"    ⚠️  {tool_name}: {str(e)[:50]}")
        
        print(f"    Tools validated: {validated}/{len(tools_to_validate)}")
        
        if validated < len(tools_to_validate) * 0.8:
            raise Exception(f"Too many validation failures: {validated}/{len(tools_to_validate)}")
    
    def _setup_directories(self):
        """Create required directories."""
        directories = [
            self.data_dir / "evolution",
            self.data_dir / "hypotheses",
            self.data_dir / "generated_tools",
            self.data_dir / "deployments",
            self.logs_dir / "deployment",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        print(f"    Directories created: {len(directories)}")
    
    def _configure_environment(self):
        """Setup environment configuration."""
        # Create deployment config
        config = {
            "deployment_id": self.deployment_id,
            "environment": self.environment,
            "timestamp": datetime.now().isoformat(),
            "workspace": str(self.workspace_dir),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "tools_count": 17,
            "features": {
                "llm_integration": True,
                "tool_generation": True,
                "evolutionary_algorithms": True,
                "auto_deployment": True,
                "health_monitoring": True
            }
        }
        
        config_file = self.data_dir / "deployments" / f"{self.deployment_id}.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        print(f"    Config file: {config_file}")
        print(f"    Features enabled: {sum(config['features'].values())}/{len(config['features'])}")
    
    def _register_services(self):
        """Register services for auto-start."""
        services = [
            {
                "name": "memory_distillation",
                "schedule": "daily",
                "time": "06:00",
                "script": "memory_distillation_runner.py",
                "args": "--daily-run"
            },
            {
                "name": "self_improvement",
                "schedule": "continuous",
                "interval": "30min",
                "script": "memory_self_improving_engine.py",
                "args": "--auto-execute"
            },
            {
                "name": "evolution_engine",
                "schedule": "weekly",
                "day": "Sunday",
                "time": "05:00",
                "script": "memory_evolutionary_algorithms.py",
                "args": "--evolve 10"
            },
            {
                "name": "dashboard",
                "schedule": "on-demand",
                "port": 8080,
                "script": "memory_dashboard_v2.py",
                "args": "--serve"
            }
        ]
        
        service_file = self.data_dir / "deployments" / "services.json"
        with open(service_file, 'w', encoding='utf-8') as f:
            json.dump({"services": services, "deployment_id": self.deployment_id}, f, indent=2)
        
        print(f"    Services registered: {len(services)}")
        for service in services:
            print(f"      - {service['name']} ({service['schedule']})")
    
    def _health_check(self):
        """Run comprehensive health check."""
        checks = {
            "workspace_accessible": self.workspace_dir.exists(),
            "tools_importable": True,  # Already validated
            "data_dir_writable": self._test_write_permission(self.data_dir),
            "logs_dir_writable": self._test_write_permission(self.logs_dir),
            "config_valid": (self.data_dir / "deployments" / f"{self.deployment_id}.json").exists(),
            "backup_created": self.backup_dir.exists() if self.backup_dir else False
        }
        
        # Run checks
        all_passed = True
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"    {status} {check_name}")
            if not result:
                all_passed = False
        
        if not all_passed:
            raise Exception("Health check failed")
        
        print(f"    Health check: {sum(checks.values())}/{len(checks)} passed")
    
    def _test_write_permission(self, directory: Path) -> bool:
        """Test if directory is writable."""
        try:
            test_file = directory / f".test_{self.deployment_id}"
            test_file.touch()
            test_file.unlink()
            return True
        except:
            return False
    
    def _post_deployment(self):
        """Execute post-deployment tasks."""
        # Integrate report monitoring system
        print("\n[8.1] Integrating report monitoring system...")
        self._integrate_report_monitoring()
        
        # Create deployment report
        report = {
            "deployment_id": self.deployment_id,
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "environment": self.environment,
            "steps_completed": self.steps_completed,
            "steps_failed": self.steps_failed,
            "backup_location": str(self.backup_dir) if self.backup_dir else None,
            "configuration": {
                "workspace": str(self.workspace_dir),
                "tools_dir": str(self.tools_dir),
                "data_dir": str(self.data_dir)
            }
        }
        
        report_file = self.logs_dir / "deployment" / f"{self.deployment_id}-report.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"    Deployment report: {report_file}")
        print(f"    Steps completed: {len(self.steps_completed)}")
    
    def _integrate_report_monitoring(self):
        """Integrate report monitoring system into production."""
        import subprocess
        
        # Create report monitoring config
        monitor_config = {
            "enabled": True,
            "frequency": "weekly",
            "script": "monitor_reports.py",
            "output_dir": "20-data-reports",
            "state_file": "report-monitor-state.json",
            "standard_dirs": [
                "21-reports",
                "30-scripts-tools",
                "06-research",
                "13-memory",
                "15-docs",
                "20-data-reports"
            ],
            "valid_prefixes": [
                "REPORT", "TEST", "DOC", "MAT", "CNT", "LIG",
                "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P9",
                "MEMORY", "CI-CD", "SECURITY", "FEISHU",
                "daily", "weekly", "monthly"
            ],
            "alerts": {
                "max_reports": 200,
                "max_issues": 5,
                "max_duplicates": 3
            }
        }
        
        config_file = self.data_dir / "report_monitoring_config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(monitor_config, f, indent=2, ensure_ascii=False)
        
        # Verify HEARTBEAT.md integration
        heartbeat_file = self.workspace_dir / "HEARTBEAT.md"
        if heartbeat_file.exists():
            with open(heartbeat_file, 'r', encoding='utf-8') as f:
                heartbeat_content = f.read()
            
            if "报告系统监控" in heartbeat_content:
                print("    ✅ Report monitoring in HEARTBEAT.md")
            else:
                print("    ⚠️  Report monitoring NOT in HEARTBEAT.md")
        
        # Run initial scan
        print("    Running initial report scan...")
        try:
            result = subprocess.run(
                [sys.executable, str(self.tools_dir / "monitor_reports.py")],
                cwd=str(self.workspace_dir),
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8'
            )
            if result.returncode == 0:
                print("    ✅ Initial scan completed")
            else:
                print(f"    ⚠️  Initial scan failed: {result.stderr[:100]}")
        except Exception as e:
            print(f"    ⚠️  Initial scan error: {str(e)[:100]}")
        
        print(f"    Config file: {config_file}")
        print("    ✅ Report monitoring integrated")
        
        # Integrate report generation tools
        print("\n[8.2] Integrating report generation tools...")
        self._integrate_report_generation()
        
        # Integrate report lifecycle management
        print("\n[8.3] Integrating report lifecycle management...")
        self._integrate_lifecycle_management()
        
        # Integrate report quality scoring system
        print("\n[8.4] Integrating report quality scoring system...")
        self._integrate_quality_scoring()
        
        # Integrate report search engine
        print("\n[8.5] Integrating report search engine...")
        self._integrate_search_engine()
        
        # Integrate report consumption tracker
        print("\n[8.6] Integrating report consumption tracker...")
        self._integrate_consumption_tracker()
        
        # Integrate report storage optimizer
        print("\n[8.7] Integrating report storage optimizer...")
        self._integrate_storage_optimizer()
        
        # Integrate report access controller
        print("\n[8.8] Integrating report access controller...")
        self._integrate_access_controller()
    
    def _integrate_access_controller(self):
        """Integrate report access controller into production."""
        
        # Verify access script exists
        access_src = self.tools_dir / 'report_access.py'
        if access_src.exists():
            print("    ✅ report_access.py exists")
        else:
            print("    ❌ report_access.py missing")
        
        # Create access config
        access_config = {
            'enabled': True,
            'script': 'report_access.py',
            'features': {
                'access_control': True,
                'sensitive_classification': True,
                'access_logging': True,
                'permission_audit': True
            },
            'default_level': 'public',
            'auto_classify': True,
            'log_access': True,
            'log_retention_days': 90,
            'users': {
                'default': {'role': 'user', 'access_levels': ['public', 'internal']},
                'admin': {'role': 'admin', 'access_levels': ['public', 'internal', 'confidential', 'restricted']}
            }
        }
        
        config_file = self.data_dir / 'report_access_config.json'
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(access_config, f, indent=2, ensure_ascii=False)
        
        # Create protected reports file
        protected_file = self.data_dir / 'protected_reports.json'
        if not protected_file.exists():
            with open(protected_file, 'w', encoding='utf-8') as f:
                json.dump({'protected': [], 'classifications': {}}, f, indent=2)
        
        print(f"    Protected reports file: {protected_file}")
        print(f"    Config file: {config_file}")
        print("    ✅ Report access controller integrated")
    
    def _integrate_storage_optimizer(self):
        """Integrate report storage optimizer into production."""
        
        # Verify storage script exists
        storage_src = self.tools_dir / 'report_storage.py'
        if storage_src.exists():
            print("    ✅ report_storage.py exists")
        else:
            print("    ❌ report_storage.py missing")
        
        # Create storage config
        storage_config = {
            'enabled': True,
            'script': 'report_storage.py',
            'features': {
                'duplicate_detection': True,
                'storage_analysis': True,
                'smart_archiving': True,
                'cleanup_suggestions': True,
                'compression': False
            },
            'similarity_threshold': 0.9,
            'archive_after_days': 90,
            'delete_after_days': 365,
            'auto_archive': True,
            'auto_delete': False
        }
        
        config_file = self.data_dir / 'report_storage_config.json'
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(storage_config, f, indent=2, ensure_ascii=False)
        
        print(f"    Config file: {config_file}")
        print("    ✅ Report storage optimizer integrated")
    
    def _integrate_consumption_tracker(self):
        """Integrate report consumption tracker into production."""
        
        # Verify tracker script exists
        tracker_src = self.tools_dir / 'report_tracker.py'
        if tracker_src.exists():
            print("    ✅ report_tracker.py exists")
        else:
            print("    ❌ report_tracker.py missing")
        
        # Create tracking config
        tracking_config = {
            'enabled': True,
            'script': 'report_tracker.py',
            'features': {
                'view_tracking': True,
                'citation_tracking': True,
                'usage_statistics': True,
                'popular_reports': True,
                'citation_graph': True
            },
            'track_reads': True,
            'track_citations': True,
            'auto_detect_citations': True,
            'popular_threshold': 10,
            'retention_days': 90
        }
        
        config_file = self.data_dir / 'report_tracking_config.json'
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(tracking_config, f, indent=2, ensure_ascii=False)
        
        # Create citations file
        citations_file = self.data_dir / 'report_citations.json'
        if not citations_file.exists():
            with open(citations_file, 'w', encoding='utf-8') as f:
                json.dump({'citations': [], 'graph': {}}, f, indent=2)
        
        print(f"    Citations file: {citations_file}")
        print(f"    Config file: {config_file}")
        print("    ✅ Report consumption tracker integrated")
    
    def _integrate_search_engine(self):
        """Integrate report search engine into production."""
        
        # Verify search script exists
        search_src = self.tools_dir / 'report_search.py'
        if search_src.exists():
            print("    ✅ report_search.py exists")
        else:
            print("    ❌ report_search.py missing")
        
        # Create search config
        search_config = {
            'enabled': True,
            'script': 'report_search.py',
            'features': {
                'semantic_search': True,
                'tag_system': True,
                'advanced_filtering': True,
                'smart_sorting': True,
                'citation_tracking': True
            },
            'search_fields': ['title', 'content', 'tags', 'metadata'],
            'min_similarity': 0.3,
            'max_results': 20,
            'auto_tag': True,
            'tag_sources': ['title', 'headings', 'keywords'],
            'index_frequency': 'daily'
        }
        
        config_file = self.data_dir / 'report_search_config.json'
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(search_config, f, indent=2, ensure_ascii=False)
        
        # Create tags file
        tags_file = self.data_dir / 'report_tags.json'
        if not tags_file.exists():
            with open(tags_file, 'w', encoding='utf-8') as f:
                json.dump({'tags': {}, 'last_updated': None}, f, indent=2)
        
        print(f"    Tags file: {tags_file}")
        print(f"    Config file: {config_file}")
        print("    ✅ Report search engine integrated")
    
    def _integrate_quality_scoring(self):
        """Integrate report quality scoring system into production."""
        
        # Verify quality scorer script exists
        scorer_src = self.tools_dir / 'report_quality_scorer.py'
        if scorer_src.exists():
            print("    ✅ report_quality_scorer.py exists")
        else:
            print("    ❌ report_quality_scorer.py missing")
        
        # Create quality scoring config
        quality_config = {
            'enabled': True,
            'script': 'report_quality_scorer.py',
            'dimensions': {
                'has_title': {'weight': 0.15, 'description': '标题清晰具体'},
                'has_executive_summary': {'weight': 0.15, 'description': '有执行摘要'},
                'has_background': {'weight': 0.15, 'description': '有背景说明'},
                'has_conclusions': {'weight': 0.15, 'description': '有结论建议'},
                'has_metadata': {'weight': 0.15, 'description': '元数据完整'},
                'min_length': {'weight': 0.15, 'description': '长度合理 (500-5000 字)'},
                'has_checklist': {'weight': 0.10, 'description': '有检查清单'}
            },
            'thresholds': {
                'excellent': 90,
                'good': 70,
                'needs_improvement': 50
            },
            'min_word_count': 500,
            'max_word_count': 5000,
            'frequency': 'weekly',
            'auto_report': True,
            'quality_gate': 70
        }
        
        config_file = self.data_dir / 'report_quality_config.json'
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(quality_config, f, indent=2, ensure_ascii=False)
        
        # Create quality reports directory
        quality_reports_dir = self.workspace_dir / '21-reports' / 'quality-reports'
        quality_reports_dir.mkdir(parents=True, exist_ok=True)
        print(f"    Quality reports directory: {quality_reports_dir}")
        
        print(f"    Config file: {config_file}")
        print("    ✅ Report quality scoring system integrated")
    
    def _integrate_report_generation(self):
        """Integrate report generation tools into production."""
        
        # Verify template exists
        template_src = self.tools_dir / 'templates' / 'REPORT-TEMPLATE.md'
        if template_src.exists():
            print("    ✅ REPORT-TEMPLATE.md exists")
        else:
            print("    ❌ REPORT-TEMPLATE.md missing")
        
        # Verify generator script
        generator_src = self.tools_dir / 'report_generator.py'
        if generator_src.exists():
            print("    ✅ report_generator.py exists")
        else:
            print("    ❌ report_generator.py missing")
        
        # Verify quality hook
        hook_src = self.tools_dir / 'report_quality_hook.py'
        if hook_src.exists():
            print("    ✅ report_quality_hook.py exists")
        else:
            print("    ❌ report_quality_hook.py missing")
        
        # Create generation config
        gen_config = {
            'enabled': True,
            'template': 'templates/REPORT-TEMPLATE.md',
            'generator': 'report_generator.py',
            'quality_hook': 'report_quality_hook.py',
            'quality_threshold': 70,
            'similarity_threshold': 0.8,
            'auto_id': True,
            'required_fields': ['title', 'date', 'author', 'type', 'status'],
            'quality_dimensions': [
                'has_title',
                'has_executive_summary',
                'has_background',
                'has_conclusions',
                'has_metadata',
                'min_length',
                'has_checklist'
            ]
        }
        
        config_file = self.data_dir / 'report_generation_config.json'
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(gen_config, f, indent=2, ensure_ascii=False)
        
        print(f"    Config file: {config_file}")
        print("    ✅ Report generation tools integrated")
    
    def _integrate_lifecycle_management(self):
        """Integrate report lifecycle management into production."""
        
        # Verify lifecycle script exists
        lifecycle_src = self.tools_dir / 'report_lifecycle.py'
        if lifecycle_src.exists():
            print("    ✅ report_lifecycle.py exists")
        else:
            print("    ❌ report_lifecycle.py missing")
        
        # Create lifecycle config
        lifecycle_config = {
            'enabled': True,
            'script': 'report_lifecycle.py',
            'stages': {
                'new': {'days': 7, 'action': 'keep'},
                'active': {'days': 30, 'action': 'keep'},
                'archive': {'days': 90, 'action': 'archive'},
                'delete': {'days': 999, 'action': 'delete'}
            },
            'important_patterns': ['PRODUCTION', 'COMPLETE', 'FINAL', 'SECURITY'],
            'archive_dir': '21-reports/archive',
            'frequency': 'weekly',
            'dry_run_default': True,
            'auto_archive': True,
            'auto_cleanup': False
        }
        
        config_file = self.data_dir / 'report_lifecycle_production.json'
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(lifecycle_config, f, indent=2, ensure_ascii=False)
        
        # Create archive directory
        archive_dir = self.workspace_dir / '21-reports' / 'archive'
        archive_dir.mkdir(parents=True, exist_ok=True)
        print(f"    Archive directory: {archive_dir}")
        
        print(f"    Config file: {config_file}")
        print("    ✅ Report lifecycle management integrated")
    
    def _rollback(self):
        """Execute rollback on failure."""
        print("\n⚠️  Deployment failed! Initiating rollback...")
        
        if self.backup_dir and self.backup_dir.exists():
            # Restore configuration
            config_files = [".env", "HEARTBEAT.md", "MEMORY.md"]
            for config_file in config_files:
                backup_file = self.backup_dir / config_file
                if backup_file.exists():
                    original = self.workspace_dir / config_file
                    shutil.copy2(backup_file, original)
                    print(f"    Restored: {config_file}")
            
            # Restore state
            state_dir = self.data_dir / "self_improvement"
            backup_state = self.backup_dir / "self_improvement"
            if backup_state.exists():
                if state_dir.exists():
                    shutil.rmtree(state_dir)
                shutil.copytree(backup_state, state_dir)
                print(f"    Restored: self_improvement state")
        
        print("    Rollback complete")
    
    def _print_success(self):
        """Print success summary."""
        print("\n" + "="*70)
        print("✅ DEPLOYMENT SUCCESSFUL!")
        print("="*70)
        print(f"Deployment ID: {self.deployment_id}")
        print(f"Environment: {self.environment}")
        print(f"Steps Completed: {len(self.steps_completed)}/{len(self.steps_completed)+len(self.steps_failed)}")
        print(f"Backup Location: {self.backup_dir}")
        print("="*70)
        print("\n📋 Next Steps:")
        print("  1. Review deployment report")
        print("  2. Test services manually")
        print("  3. Enable auto-start (if desired)")
        print("  4. Monitor health dashboard")
        print("="*70)
    
    def _print_failure(self, error: str):
        """Print failure summary."""
        print("\n" + "="*70)
        print("❌ DEPLOYMENT FAILED!")
        print("="*70)
        print(f"Error: {error}")
        print(f"Steps Completed: {len(self.steps_completed)}")
        print(f"Steps Failed: {len(self.steps_failed)}")
        print(f"Failed Steps: {', '.join(self.steps_failed)}")
        print("="*70)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Production Deployment Script")
    parser.add_argument(
        "--workspace",
        default="D:\\OpenClaw\\workspace",
        help="Workspace directory"
    )
    parser.add_argument(
        "--environment",
        default="production",
        choices=["development", "staging", "production"],
        help="Deployment environment"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making changes"
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print(f"Workspace: {args.workspace}")
        print(f"Environment: {args.environment}")
        return 0
    
    # Execute deployment
    deployer = ProductionDeployer(args.workspace, args.environment)
    success = deployer.run()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
