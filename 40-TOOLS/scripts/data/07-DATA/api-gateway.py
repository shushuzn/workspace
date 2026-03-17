#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Gateway Service with Authentication
API 网关服务 (带认证)
"""

from flask import Flask, jsonify, request, abort
from functools import wraps
from pathlib import Path
import json
import os
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.cache_manager import CacheManager, cached
from utils.retry_manager import retry, RetryManager
from utils.input_validator import InputValidator, ValidationError
from utils.performance_optimizer import PerformanceOptimizer, timed

# 初始化缓存
cache = CacheManager(ttl_seconds=300)  # 5 分钟 TTL

# 初始化重试管理器
retry_manager = RetryManager(max_attempts=3, delay_seconds=1, backoff_factor=2)

# 初始化输入验证器
validator = InputValidator()

# 初始化性能优化器
perf_optimizer = PerformanceOptimizer()

app = Flask(__name__)

# 配置
API_KEY = os.environ.get('API_KEY', 'dev-key-12345')  # 默认开发密钥
RATE_LIMIT = 60  # 每分钟请求数

# 数据目录
DATA_DIR = Path(__file__).parent.parent

def require_api_key(f):
    """API 密钥认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            abort(401, description='Missing API key')
        if api_key != API_KEY:
            abort(403, description='Invalid API key')
        return f(*args, **kwargs)
    return decorated

def rate_limit(f):
    """速率限制装饰器 (简化版)"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # TODO: 实现真正的速率限制
        return f(*args, **kwargs)
    return decorated

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request', 'message': error.description}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized', 'message': error.description}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden', 'message': error.description}), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found', 'message': error.description}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error', 'message': 'An unexpected error occurred'}), 500

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0',
        'auth_enabled': True
    })

@app.route('/api/v1/papers', methods=['GET'])
@require_api_key
@rate_limit
@retry(max_attempts=3, delay_seconds=0.5, backoff_factor=2)
@timed
def get_papers():
    """获取论文数据 (带重试和性能分析)"""
    try:
        date = request.args.get('date', '')
        
        # 输入验证
        if date:
            try:
                validator.validate_date(date)
            except ValidationError as e:
                abort(400, description=str(e))
        
        cache_key = f'papers:{date}'
        
        # 性能优化：使用优化器加载数据
        def load_papers():
            if date:
                papers_file = DATA_DIR / 'obsidian-vault' / 'Arxiv' / 'daily' / date / 'quality-controlled' / 'validated_papers.json'
            else:
                papers_file = DATA_DIR / 'data-lake' / 'analytics' / 'latest_papers.json'
            
            if papers_file.exists():
                with open(papers_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        
        # 尝试从缓存获取
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            app.logger.info(f"Cache hit for {cache_key}")
            return jsonify(cached_data)
        
        # 使用性能优化器加载数据
        papers = perf_optimizer.optimize_data_loading(load_papers, cache_key, ttl=300)
        
        if papers:
            # 保存到缓存
            cache.set(cache_key, papers)
            return jsonify(papers)
        else:
            abort(404, description='No data found')
    except ValidationError:
        raise
    except Exception as e:
        app.logger.error(f"Error getting papers: {e}")
        abort(500)

@app.route('/api/v1/trends', methods=['GET'])
@require_api_key
@rate_limit
def get_trends():
    """获取趋势数据"""
    try:
        date = request.args.get('date', '')
        cache_key = f'trends:{date}'
        
        # 尝试从缓存获取
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            app.logger.info(f"Cache hit for {cache_key}")
            return jsonify(cached_data)
        
        # 从文件加载
        if date:
            trends_file = DATA_DIR / 'obsidian-vault' / 'Arxiv' / 'daily' / date / 'trends' / 'trends.json'
        else:
            trends_file = DATA_DIR / 'data-lake' / 'analytics' / 'latest_trends.json'
        
        if trends_file.exists():
            with open(trends_file, 'r', encoding='utf-8') as f:
                trends = json.load(f)
            
            # 保存到缓存
            cache.set(cache_key, trends)
            return jsonify(trends)
        else:
            abort(404, description='No data found')
    except Exception as e:
        app.logger.error(f"Error getting trends: {e}")
        abort(500)

@app.route('/api/v1/clusters', methods=['GET'])
@require_api_key
@rate_limit
def get_clusters():
    """获取聚类数据"""
    try:
        date = request.args.get('date', '')
        
        if date:
            clusters_file = DATA_DIR / 'obsidian-vault' / 'Arxiv' / 'daily' / date / 'clusters' / 'clusters.json'
        else:
            clusters_file = DATA_DIR / 'data-lake' / 'analytics' / 'latest_clusters.json'
        
        if clusters_file.exists():
            with open(clusters_file, 'r', encoding='utf-8') as f:
                clusters = json.load(f)
            return jsonify(clusters)
        else:
            abort(404, description='No data found')
    except Exception as e:
        app.logger.error(f"Error getting clusters: {e}")
        abort(500)

@app.route('/api/v1/graph', methods=['GET'])
@require_api_key
@rate_limit
def get_knowledge_graph():
    """获取知识图谱数据"""
    try:
        graph_file = DATA_DIR / 'knowledge-graph' / 'materials-kg.json'
        
        if graph_file.exists():
            with open(graph_file, 'r', encoding='utf-8') as f:
                graph = json.load(f)
            return jsonify(graph)
        else:
            abort(404, description='No data found')
    except Exception as e:
        app.logger.error(f"Error getting graph: {e}")
        abort(500)

@app.route('/api/v1/metrics', methods=['GET'])
@require_api_key
@rate_limit
def get_metrics():
    """获取监控指标"""
    try:
        metrics_file = DATA_DIR / 'monitoring' / 'metrics.json'
        
        if metrics_file.exists():
            with open(metrics_file, 'r', encoding='utf-8') as f:
                metrics = json.load(f)
            return jsonify(metrics)
        else:
            abort(404, description='No data found')
    except Exception as e:
        app.logger.error(f"Error getting metrics: {e}")
        abort(500)

@app.route('/api/v1/alerts', methods=['GET'])
@require_api_key
@rate_limit
def get_alerts():
    """获取告警数据"""
    try:
        alerts_file = DATA_DIR / 'monitoring' / 'alerts.json'
        
        if alerts_file.exists():
            with open(alerts_file, 'r', encoding='utf-8') as f:
                alerts = json.load(f)
            return jsonify(alerts)
        else:
            abort(404, description='No data found')
    except Exception as e:
        app.logger.error(f"Error getting alerts: {e}")
        abort(500)

if __name__ == '__main__':
    print("=" * 60)
    print("API Gateway Service v2.0 (with Authentication)")
    print("=" * 60)
    print("\nSecurity:")
    print(f"  API Key: {'*' * len(API_KEY)}")
    print(f"  Rate Limit: {RATE_LIMIT} requests/minute")
    print("\nStarting API server...")
    print("\nEndpoints:")
    print("  GET /api/v1/health     - Health check (no auth)")
    print("  GET /api/v1/papers     - Get papers data (auth required)")
    print("  GET /api/v1/trends     - Get trends data (auth required)")
    print("  GET /api/v1/clusters   - Get clusters data (auth required)")
    print("  GET /api/v1/graph      - Get knowledge graph (auth required)")
    print("  GET /api/v1/metrics    - Get monitoring metrics (auth required)")
    print("  GET /api/v1/alerts     - Get alerts (auth required)")
    print("\nServer running on http://localhost:5000")
    print("\nExample:")
    print(f"  curl -H 'X-API-Key: {API_KEY}' http://localhost:5000/api/v1/health")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
