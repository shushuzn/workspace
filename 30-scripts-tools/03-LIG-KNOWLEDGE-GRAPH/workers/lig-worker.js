/**
 * LIG Knowledge Graph - FDEB Worker
 * 
 * Force-Directed Edge Bundling 后台计算线程
 * 负责密集的边捆绑计算，避免阻塞主线程 UI
 * 
 * @author Claw (AI Research OS)
 * @version 1.0.0
 * @date 2026-03-09
 */

// ==================== 配置参数 ====================
let config = {
    bundlingStrength: 0.6,  // Bundling 强度 (0-1)
    divisions: 5,           // 边分割段数 (3-10)
    iterations: 15,         // 迭代次数 (5-30)
    compatibilityThreshold: 0.5,  // 边兼容性阈值
    debug: false            // 调试模式 (输出日志)
};

// 停止标志
let shouldStop = false;

// ==================== 工具函数 ====================

/**
 * 调试日志输出 (仅调试模式启用)
 */
function debugLog(...args) {
    if (config.debug) {
        console.log('[FDEB Worker]', ...args);
    }
}

/**
 * 计算两点间距离
 */
function distance(x1, y1, x2, y2) {
    return Math.hypot(x2 - x1, y2 - y1);
}

/**
 * 计算边兼容性 (三维度量)
 * @param {Object} e1 - 边 1
 * @param {Object} e2 - 边 2
 * @param {Array} nodes - 节点数组
 * @returns {number} 兼容性分数 (0-1)
 */
function computeCompatibility(e1, e2, nodes) {
    if (!e1.controlPoints || !e2.controlPoints || 
        e1.controlPoints.length === 0 || e2.controlPoints.length === 0) {
        return 0;
    }
    
    // 1. 角度兼容性 (方向相似度)
    const cp1 = e1.controlPoints[0];
    const cp2 = e2.controlPoints[0];
    const angle1 = Math.atan2(cp1.y, cp1.x);
    const angle2 = Math.atan2(cp2.y, cp2.x);
    const angleDiff = Math.abs(angle1 - angle2);
    const angleComp = 1 - (angleDiff / Math.PI);
    
    // 2. 长度兼容性
    const src1 = getNodeById(nodes, e1.source);
    const tgt1 = getNodeById(nodes, e1.target);
    const src2 = getNodeById(nodes, e2.source);
    const tgt2 = getNodeById(nodes, e2.target);
    
    const len1 = distance(src1.x, src1.y, tgt1.x, tgt1.y);
    const len2 = distance(src2.x, src2.y, tgt2.x, tgt2.y);
    const maxLen = Math.max(len1, len2, 1);
    const lenComp = 1 - Math.abs(len1 - len2) / maxLen;
    
    // 3. 位置兼容性 (源点距离)
    const srcDist = distance(src1.x, src1.y, src2.x, src2.y);
    const posComp = 1 / (1 + srcDist / 200);
    
    // 加权平均
    const compatibility = (angleComp + lenComp + posComp) / 3;
    
    debugLog(`Edge ${e1.id}-${e2.id} compatibility: ${compatibility.toFixed(3)}`);
    
    return compatibility;
}

/**
 * 通过 ID 获取节点
 */
function getNodeById(nodes, id) {
    const node = nodes.find(n => n.id === id);
    return node || {x: 0, y: 0};
}

// ==================== 核心算法 ====================

/**
 * 初始化边的控制点 (均匀分布在源和目标之间)
 */
function initControlPoints(edges, nodes) {
    debugLog(`Initializing control points for ${edges.length} edges, divisions=${config.divisions}`);
    
    for (const edge of edges) {
        edge.controlPoints = [];
        const src = getNodeById(nodes, edge.source);
        const tgt = getNodeById(nodes, edge.target);
        
        for (let i = 1; i < config.divisions; i++) {
            const t = i / config.divisions;
            edge.controlPoints.push({
                x: src.x + (tgt.x - src.x) * t,
                y: src.y + (tgt.y - src.y) * t
            });
        }
    }
    
    debugLog(`Initialized ${edges.length * (config.divisions - 1)} control points`);
}

/**
 * FDEB 主迭代优化
 * 
 * 算法流程:
 * 1. 对每条边的每个控制点施加弹簧力 (保持均匀分布)
 * 2. 对兼容的边施加吸引力 (平行边汇聚)
 * 3. 迭代优化直到收敛或达到最大迭代次数
 */
function applyFDEB(edges, nodes, onProgress) {
    const springStrength = 0.05;
    const attractionStrength = config.bundlingStrength * 0.02;
    
    debugLog(`Starting FDEB: iterations=${config.iterations}, strength=${config.bundlingStrength}`);
    
    for (let iter = 0; iter < config.iterations && !shouldStop; iter++) {
        const startTime = performance.now();
        
        for (const edge of edges) {
            for (let i = 0; i < edge.controlPoints.length; i++) {
                const cp = edge.controlPoints[i];
                let fx = 0, fy = 0;
                
                // 1. 弹簧力 (保持控制点均匀分布)
                if (i > 0) {
                    const prev = edge.controlPoints[i - 1];
                    fx += (prev.x - cp.x) * springStrength;
                    fy += (prev.y - cp.y) * springStrength;
                }
                if (i < edge.controlPoints.length - 1) {
                    const next = edge.controlPoints[i + 1];
                    fx += (next.x - cp.x) * springStrength;
                    fy += (next.y - cp.y) * springStrength;
                }
                
                // 2. 吸引力 (平行边相互汇聚)
                for (const other of edges) {
                    if (edge === other || other.controlPoints.length <= i) {
                        continue;
                    }
                    
                    const compat = computeCompatibility(edge, other, nodes);
                    if (compat < config.compatibilityThreshold) {
                        continue;
                    }
                    
                    const ocp = other.controlPoints[i];
                    const dx = ocp.x - cp.x;
                    const dy = ocp.y - cp.y;
                    const dist = distance(cp.x, cp.y, ocp.x, ocp.y);
                    
                    if (dist > 0 && dist < 150) {
                        const force = attractionStrength * compat / dist;
                        fx += dx * force;
                        fy += dy * force;
                    }
                }
                
                // 更新控制点位置
                cp.x += fx;
                cp.y += fy;
            }
        }
        
        const endTime = performance.now();
        const iterTime = (endTime - startTime).toFixed(2);
        debugLog(`Iteration ${iter + 1}/${config.iterations} completed in ${iterTime}ms`);
        
        // 发送进度更新
        const progress = (iter + 1) / config.iterations * 100;
        if (onProgress) {
            onProgress(progress, edges);
        }
    }
    
    if (shouldStop) {
        debugLog('FDEB stopped by user');
    } else {
        debugLog('FDEB completed successfully');
    }
}

/**
 * 生成 B 样条路径 (用于 D3 渲染)
 */
function generateBSplinePath(edge, nodes) {
    const src = getNodeById(nodes, edge.source);
    const tgt = getNodeById(nodes, edge.target);
    
    if (!edge.controlPoints || edge.controlPoints.length === 0) {
        return `M${src.x},${src.y}L${tgt.x},${tgt.y}`;
    }
    
    const points = [src, ...edge.controlPoints, tgt];
    let path = `M${points[0].x},${points[0].y}`;
    
    // 二次 B 样条插值
    for (let i = 1; i < points.length - 1; i++) {
        const xc = (points[i].x + points[i + 1].x) / 2;
        const yc = (points[i].y + points[i + 1].y) / 2;
        path += ` Q${points[i].x},${points[i].y} ${xc},${yc}`;
    }
    
    path += `L${tgt.x},${tgt.y}`;
    return path;
}

// ==================== 消息处理 ====================

/**
 * 处理主线程消息
 */
self.onmessage = function(e) {
    const { type, data } = e.data;
    
    debugLog(`Received message: ${type}`, data);
    
    switch (type) {
        case 'CONFIG':
            // 更新配置
            if (data.bundlingStrength !== undefined) {
                config.bundlingStrength = data.bundlingStrength;
            }
            if (data.divisions !== undefined) {
                config.divisions = data.divisions;
            }
            if (data.iterations !== undefined) {
                config.iterations = data.iterations;
            }
            if (data.debug !== undefined) {
                config.debug = data.debug;
            }
            
            debugLog('Config updated:', config);
            self.postMessage({ type: 'CONFIG_UPDATED', config });
            break;
            
        case 'RUN_FDEB': {
            // 开始 FDEB 计算
            shouldStop = false;
            const { nodes, links } = data;
            
            debugLog(`Starting FDEB with ${nodes.length} nodes and ${links.length} links`);
            
            // 初始化边数据结构
            const edges = links.map((link, idx) => ({
                id: idx,
                source: link.source,
                target: link.target,
                value: link.value,
                controlPoints: []
            }));
            
            // 初始化控制点
            initControlPoints(edges, nodes);
            
            // 运行 FDEB 优化
            applyFDEB(edges, nodes, (progress, updatedEdges) => {
                // 发送进度更新 (限制频率避免过多消息)
                if (Math.round(progress) % 10 === 0 || progress >= 100) {
                    self.postMessage({
                        type: 'PROGRESS',
                        progress: progress,
                        edges: updatedEdges
                    });
                }
            });
            
            // 发送最终结果
            if (!shouldStop) {
                self.postMessage({
                    type: 'COMPLETE',
                    edges: edges
                });
            } else {
                self.postMessage({ type: 'STOPPED' });
            }
            break;
        }
        
        case 'STOP':
            // 停止计算
            shouldStop = true;
            debugLog('Stop requested');
            break;
            
        case 'DEBUG':
            // 切换调试模式
            config.debug = data.enabled;
            debugLog(`Debug mode ${config.debug ? 'enabled' : 'disabled'}`);
            break;
            
        default:
            console.warn('[FDEB Worker] Unknown message type:', type);
    }
};

/**
 * Worker 错误处理
 */
self.onerror = function(error) {
    console.error('[FDEB Worker] Error:', error);
    self.postMessage({
        type: 'ERROR',
        message: error.message,
        filename: error.filename,
        lineno: error.lineno,
        colno: error.colno
    });
};

// ==================== 生命周期 ====================

debugLog('FDEB Worker initialized');
debugLog('Default config:', config);

// 发送就绪消息
self.postMessage({ type: 'READY' });
