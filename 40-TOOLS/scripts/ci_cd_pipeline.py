#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CI/CD Pipeline Generator - Automated CI/CD configuration

Features:
- GitHub Actions workflow generation
- GitLab CI configuration
- Jenkins pipeline generation
- Multi-language support
- Test integration
- Deployment automation
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import yaml

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
CI_CD_DIR = WORKSPACE / '.github' / 'workflows'
CI_CD_DIR.mkdir(parents=True, exist_ok=True)

class CICDPipeline:
    """CI/CD Pipeline configuration generator"""
    
    # Template configurations
    TEMPLATES = {
        'python': {
            'test_command': 'pytest tests/ -v --cov=src',
            'lint_command': 'flake8 src/ tests/',
            'build_command': 'python setup.py sdist bdist_wheel',
            'dependencies_file': 'requirements.txt',
        },
        'nodejs': {
            'test_command': 'npm test',
            'lint_command': 'npm run lint',
            'build_command': 'npm run build',
            'dependencies_file': 'package.json',
        },
        'docker': {
            'build_command': 'docker build -t app:latest .',
            'test_command': 'docker-compose run test',
            'push_command': 'docker push app:latest',
            'dependencies_file': 'requirements.txt',
        },
        'static': {
            'lint_command': 'echo "No linting for static files"',
            'test_command': 'echo "No tests for static files"',
            'build_command': 'echo "No build for static files"',
            'dependencies_file': 'requirements.txt',
        },
    }
    
    def __init__(self, project_type: str = 'python'):
        self.project_type = project_type
        self.template = self.TEMPLATES.get(project_type, self.TEMPLATES['static'])
    
    def generate_github_actions(self, workflow_name: str = 'CI/CD Pipeline',
                                branches: List[str] = None,
                                enable_deploy: bool = False) -> str:
        """
        Generate GitHub Actions workflow
        
        Args:
            workflow_name: Workflow name
            branches: Branches to trigger on
            enable_deploy: Enable deployment step
        
        Returns:
            YAML workflow content
        """
        if branches is None:
            branches = ['main', 'master']
        
        workflow = {
            'name': workflow_name,
            'on': {
                'push': {
                    'branches': branches,
                },
                'pull_request': {
                    'branches': branches,
                },
            },
            'jobs': {
                'build': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {
                            'name': 'Checkout code',
                            'uses': 'actions/checkout@v3',
                        },
                        {
                            'name': 'Set up Python',
                            'uses': 'actions/setup-python@v4',
                            'with': {
                                'python-version': '3.11',
                            },
                        },
                        {
                            'name': 'Install dependencies',
                            'run': f'pip install -r {self.template["dependencies_file"]}',
                        },
                        {
                            'name': 'Lint',
                            'run': self.template.get('lint_command', 'echo "No lint"'),
                        },
                        {
                            'name': 'Test',
                            'run': self.template.get('test_command', 'echo "No tests"'),
                        },
                        {
                            'name': 'Build',
                            'run': self.template.get('build_command', 'echo "No build"'),
                        },
                    ],
                },
            },
        }
        
        # Add deployment step
        if enable_deploy:
            workflow['jobs']['build']['steps'].append({
                'name': 'Deploy to production',
                'run': 'python 30-scripts-tools/auto_deployer.py --deploy',
                'if': 'github.ref == \'refs/heads/main\'',
                'env': {
                    'DEPLOY_TOKEN': '${{ secrets.DEPLOY_TOKEN }}',
                    'SERVER_HOST': '${{ secrets.SERVER_HOST }}',
                },
            })
        
        return yaml.dump(workflow, default_flow_style=False, sort_keys=False)
    
    def generate_gitlab_ci(self, enable_deploy: bool = False) -> str:
        """Generate GitLab CI configuration"""
        config = {
            'stages': ['test', 'build', 'deploy'],
            'variables': {
                'PYTHON_VERSION': '3.11',
            },
        }
        
        # Test job
        config['test'] = {
            'stage': 'test',
            'image': f'python:{self.template.get("PYTHON_VERSION", "3.11")}',
            'script': [
                f'pip install -r {self.template["dependencies_file"]}',
                self.template.get('lint_command', 'echo "No lint"'),
                self.template.get('test_command', 'echo "No tests"'),
            ],
        }
        
        # Build job
        config['build'] = {
            'stage': 'build',
            'image': f'python:{self.template.get("PYTHON_VERSION", "3.11")}',
            'script': [
                self.template.get('build_command', 'echo "No build"'),
            ],
            'artifacts': {
                'paths': ['dist/'],
            },
        }
        
        # Deploy job
        if enable_deploy:
            config['deploy'] = {
                'stage': 'deploy',
                'image': 'python:3.11',
                'script': [
                    'python 30-scripts-tools/auto_deployer.py --deploy',
                ],
                'only': ['main', 'master'],
                'environment': {
                    'name': 'production',
                },
            }
        
        return yaml.dump(config, default_flow_style=False, sort_keys=False)
    
    def generate_jenkinsfile(self, enable_deploy: bool = False) -> str:
        """Generate Jenkinsfile"""
        jenkinsfile = f'''pipeline {{
    agent any
    
    environment {{
        PYTHON_VERSION = '3.11'
    }}
    
    stages {{
        stage('Checkout') {{
            steps {{
                checkout scm
            }}
        }}
        
        stage('Install Dependencies') {{
            steps {{
                sh 'pip install -r {self.template["dependencies_file"]}'
            }}
        }}
        
        stage('Lint') {{
            steps {{
                sh '{self.template.get("lint_command", "echo No lint")}'
            }}
        }}
        
        stage('Test') {{
            steps {{
                sh '{self.template.get("test_command", "echo No tests")}'
            }}
        }}
        
        stage('Build') {{
            steps {{
                sh '{self.template.get("build_command", "echo No build")}'
            }}
        }}
        
        {'''
        stage('Deploy') {
            steps {
                sh 'python 30-scripts-tools/auto_deployer.py --deploy'
            }
            when {
                branch 'main'
            }
        }
        ''' if enable_deploy else ''}
    }}
    
    post {{
        always {{
            echo 'Pipeline completed'
        }}
        success {{
            echo 'Deployment successful'
        }}
        failure {{
            echo 'Pipeline failed'
        }}
    }}
}}
'''
        return jenkinsfile


class CICDGenerator:
    """
    CI/CD Pipeline Generator
    
    Features:
    - Multiple platform support
    - Template-based generation
    - Auto-detection
    - Configuration validation
    """
    
    def __init__(self, workspace: Path = None):
        self.workspace = workspace or WORKSPACE
        self.github_dir = self.workspace / '.github' / 'workflows'
        self.gitlab_file = self.workspace / '.gitlab-ci.yml'
        self.jenkins_file = self.workspace / 'Jenkinsfile'
    
    def detect_project_type(self) -> str:
        """Auto-detect project type"""
        if (self.workspace / 'requirements.txt').exists():
            return 'python'
        elif (self.workspace / 'package.json').exists():
            return 'nodejs'
        elif (self.workspace / 'Dockerfile').exists():
            return 'docker'
        else:
            return 'static'
    
    def generate(self, platform: str = 'github', project_type: str = None,
                enable_deploy: bool = True) -> Path:
        """
        Generate CI/CD configuration
        
        Args:
            platform: Platform (github/gitlab/jenkins)
            project_type: Project type (python/nodejs/docker/static)
            enable_deploy: Enable deployment steps
        
        Returns:
            Path to generated file
        """
        if project_type is None:
            project_type = self.detect_project_type()
        
        pipeline = CICDPipeline(project_type)
        
        if platform == 'github':
            content = pipeline.generate_github_actions(enable_deploy=enable_deploy)
            output_file = self.github_dir / 'ci-cd-pipeline.yml'
        
        elif platform == 'gitlab':
            content = pipeline.generate_gitlab_ci(enable_deploy=enable_deploy)
            output_file = self.gitlab_file
        
        elif platform == 'jenkins':
            content = pipeline.generate_jenkinsfile(enable_deploy=enable_deploy)
            output_file = self.jenkins_file
        
        else:
            raise ValueError(f"Unknown platform: {platform}")
        
        # Write file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ {platform.upper()} CI/CD configuration generated: {output_file}")
        return output_file
    
    def generate_all(self, project_type: str = None, enable_deploy: bool = True) -> List[Path]:
        """Generate configurations for all platforms"""
        files = []
        
        for platform in ['github', 'gitlab', 'jenkins']:
            try:
                file_path = self.generate(platform, project_type, enable_deploy)
                files.append(file_path)
            except Exception as e:
                print(f"⚠️  Failed to generate {platform}: {e}")
        
        return files
    
    def validate(self, platform: str = 'github') -> Dict:
        """Validate CI/CD configuration"""
        if platform == 'github':
            config_file = self.github_dir / 'ci-cd-pipeline.yml'
        elif platform == 'gitlab':
            config_file = self.gitlab_file
        elif platform == 'jenkins':
            config_file = self.jenkins_file
        else:
            return {'valid': False, 'error': 'Unknown platform'}
        
        if not config_file.exists():
            return {
                'valid': False,
                'error': f'Configuration file not found: {config_file}',
            }
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic validation
            if platform in ['github', 'gitlab']:
                yaml.safe_load(content)  # Validate YAML syntax
            
            return {
                'valid': True,
                'file': str(config_file),
                'size_bytes': config_file.stat().st_size,
            }
        
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
            }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="CI/CD Pipeline Generator")
    parser.add_argument('--generate', type=str, help='Generate for platform (github/gitlab/jenkins)')
    parser.add_argument('--all', action='store_true', help='Generate for all platforms')
    parser.add_argument('--type', type=str, help='Project type (python/nodejs/docker/static)')
    parser.add_argument('--no-deploy', action='store_true', help='Disable deployment steps')
    parser.add_argument('--validate', type=str, help='Validate configuration')
    parser.add_argument('--detect', action='store_true', help='Detect project type')
    args = parser.parse_args()
    
    generator = CICDGenerator()
    
    if args.detect:
        project_type = generator.detect_project_type()
        print(f"\n🔍 Detected project type: {project_type}")
    
    elif args.generate:
        generator.generate(args.generate, args.type, not args.no_deploy)
    
    elif args.all:
        files = generator.generate_all(args.type, not args.no_deploy)
        print(f"\n✅ Generated {len(files)} configuration files")
    
    elif args.validate:
        result = generator.validate(args.validate)
        if result['valid']:
            print(f"\n✅ Configuration valid: {result['file']} ({result['size_bytes']} bytes)")
        else:
            print(f"\n❌ Configuration invalid: {result['error']}")
            sys.exit(1)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
