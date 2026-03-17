#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arxiv-ops CLI
命令行工具 for AI Research OS
"""

import click
import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

@click.group()
@click.version_option(version='2.0.0')
def cli():
    """AI Research OS 命令行工具"""
    pass

@cli.command()
def health():
    """健康检查"""
    import requests
    
    try:
        response = requests.get('http://localhost:5000/api/v1/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            click.echo(click.style('✓', fg='green') + f" 系统健康 (版本：{data.get('version', 'unknown')})")
            sys.exit(0)
        else:
            click.echo(click.style('✗', fg='red') + f" 系统异常 (状态码：{response.status_code})")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        click.echo(click.style('✗', fg='red') + f" 无法连接系统：{e}")
        sys.exit(1)

@cli.command()
@click.option('--date', default=None, help='收集日期 (YYYY-MM-DD)')
@click.option('--async', 'async_mode', is_flag=True, help='异步执行')
def collect(date, async_mode):
    """触发论文收集"""
    click.echo("开始论文收集...")
    
    # TODO: 调用收集 API
    click.echo(click.style('✓', fg='green') + " 收集任务已启动")

@cli.command()
@click.option('--date', default=None, help='检查日期')
def quality(date):
    """查看质量报告"""
    log_file = Path('logs/quality-control.log')
    
    if not log_file.exists():
        click.echo(click.style('✗', fg='red') + " 质量日志不存在")
        sys.exit(1)
    
    # 读取最后 10 行
    with open(log_file, 'r') as f:
        lines = f.readlines()[-10:]
    
    click.echo("质量报告 (最近 10 行):")
    click.echo(''.join(lines))

@cli.command()
@click.option('--format', 'output_format', type=click.Choice(['json', 'text']), default='text')
def metrics(output_format):
    """查看系统指标"""
    import requests
    
    try:
        response = requests.get('http://localhost:5000/api/v1/metrics', timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            if output_format == 'json':
                click.echo(json.dumps(data, indent=2))
            else:
                click.echo("系统指标:")
                click.echo(f"  API 请求数：{data.get('counters', {}).get('api_requests_total', 0)}")
                click.echo(f"  API 错误数：{data.get('counters', {}).get('api_errors_total', 0)}")
                click.echo(f"  CPU 使用率：{data.get('gauges', {}).get('cpu_usage', 0):.1f}%")
                click.echo(f"  内存使用率：{data.get('gauges', {}).get('memory_usage', 0):.1f}%")
        else:
            click.echo(click.style('✗', fg='red') + f" 获取指标失败 (状态码：{response.status_code})")
    except requests.exceptions.RequestException as e:
        click.echo(click.style('✗', fg='red') + f" 无法连接系统：{e}")

@cli.command()
@click.option('--severity', type=click.Choice(['warning', 'error', 'critical']))
@click.option('--limit', default=10, help='显示数量')
def alerts(severity, limit):
    """查看告警"""
    import requests
    
    try:
        url = f'http://localhost:5000/api/v1/alerts?limit={limit}'
        if severity:
            url += f'&severity={severity}'
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            alerts = data.get('alerts', [])
            
            if not alerts:
                click.echo(click.style('✓', fg='green') + " 无告警")
            else:
                click.echo(f"告警列表 (共 {len(alerts)} 条):")
                for alert in alerts:
                    severity_color = {
                        'warning': 'yellow',
                        'error': 'red',
                        'critical': 'red'
                    }.get(alert['severity'], 'white')
                    
                    click.echo(click.style(f"[{alert['severity'].upper()}]", fg=severity_color) + 
                             f" {alert['name']}: {alert['metric']}={alert['value']}")
        else:
            click.echo(click.style('✗', fg='red') + f" 获取告警失败 (状态码：{response.status_code})")
    except requests.exceptions.RequestException as e:
        click.echo(click.style('✗', fg='red') + f" 无法连接系统：{e}")

@cli.group()
def config():
    """配置管理"""
    pass

@config.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """设置配置项"""
    # TODO: 实现配置设置
    click.echo(f"设置配置：{key} = {value}")

@config.command()
@click.argument('key')
def get(key):
    """获取配置项"""
    # TODO: 实现配置获取
    click.echo(f"获取配置：{key}")

@config.command()
def show():
    """显示所有配置"""
    config_file = Path('config.yaml')
    
    if not config_file.exists():
        click.echo(click.style('✗', fg='red') + " 配置文件不存在")
        sys.exit(1)
    
    with open(config_file, 'r') as f:
        click.echo(f.read())

@cli.command()
def logs():
    """查看日志"""
    import subprocess
    
    log_dir = Path('logs')
    if not log_dir.exists():
        click.echo(click.style('✗', fg='red') + " 日志目录不存在")
        sys.exit(1)
    
    # 列出日志文件
    log_files = list(log_dir.glob('*.log'))
    click.echo("日志文件:")
    for log_file in log_files:
        click.echo(f"  - {log_file.name}")
    
    # 显示最新日志
    if log_files:
        latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
        click.echo(f"\n最新日志 ({latest_log.name}):")
        subprocess.run(['tail', '-n', '20', str(latest_log)])

@cli.command()
def status():
    """系统状态"""
    import requests
    
    click.echo("系统状态:")
    click.echo("=" * 40)
    
    # 健康检查
    try:
        response = requests.get('http://localhost:5000/api/v1/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            click.echo(click.style('  健康状态:', fg='green') + f" ✓ {data.get('version', 'unknown')}")
        else:
            click.echo(click.style('  健康状态:', fg='red') + f" ✗ (状态码：{response.status_code})")
    except:
        click.echo(click.style('  健康状态:', fg='red') + " ✗ (无法连接)")
    
    # 指标
    try:
        response = requests.get('http://localhost:5000/api/v1/metrics', timeout=5)
        if response.status_code == 200:
            data = response.json()
            click.echo(click.style('  API 请求:', fg='green') + f" {data.get('counters', {}).get('api_requests_total', 0)}")
            click.echo(click.style('  CPU:', fg='green') + f" {data.get('gauges', {}).get('cpu_usage', 0):.1f}%")
            click.echo(click.style('  内存:', fg='green') + f" {data.get('gauges', {}).get('memory_usage', 0):.1f}%")
    except:
        click.echo(click.style('  指标:', fg='red') + " ✗ (无法获取)")
    
    click.echo("=" * 40)

if __name__ == '__main__':
    cli()
