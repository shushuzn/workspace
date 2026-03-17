/**
 * LIG Knowledge Graph - FDEB Worker (Transferable 优化版)
 * 
 * 使用 ArrayBuffer 零拷贝传输，大幅提升大数据集性能
 * 
 * 内存布局:
 * - nodes: [x0, y0, x1, y1, ...] Float32 (每个节点 2 个 float)
 * - edges: [srcIdx0, tgtIdx0, srcIdx1, tgtIdx1, ...] Int32 (每条边 2 个 int)
 * - controlPoints: [cp0x, cp0y, cp1x, cp1y, ...] Float32 (每个控制点 2 个 float)
 * 
 * @author Claw (AI Research OS)
 * @version 2.0.0 (Transferable)
 * @date 2026-03-09
 */

// ==================== 配置参数 ====================
let config = {
    bundlingStrength: 0.6,
    divisions: 5,
    iterations: 15,
    compatibilityThreshold: 0.5,
    debug: false,
    // 混合模式配置
    transferableThreshold: 50,  // 节点数阈值 (>=50 用 Transferable)
    autoMode: true               // 自动选择模式
};

// 停止标志
let shouldStop = false;

// 性能统计
let perfStats = {
    serializeTime: 0,
    computeTime: 0,
    transferTime: 0,
    totalEdges: 0,
    totalControlPoints: 0
};

// ==================== 工具函数 ====================

function debugLog(...args) {
    if (config.debug) {
        console.log('[FDEB Worker]', ...args);
    }
}

function distance(x1, y1, x2, y2) {
    return Math.hypot(x2 - x1, y2 - y1);
}

/**
 * 从 ArrayBuffer 读取节点数据
 */
function parseNodes(buffer) {
    const view = new DataView(buffer);
    const nodeCount = view.getUint32(0, true);
    const nodes = [];
    
    let offset = 4;
    for (let i = 0; i < nodeCount; i++) {
        const idLen = view.getUint8(offset);
        offset++;
        const idBytes = new Uint8Array(buffer, offset, idLen);
        const id = new TextDecoder().decode(idBytes);
        offset += idLen;
        const x = view.getFloat32(offset, true);
        offset += 4;
        const y = view.getFloat32(offset, true);
        offset += 4;
        
        nodes.push({ id, x, y });
    }
    
    return nodes;
}

/**
 * 序列化节点为 ArrayBuffer
 */
function serializeNodesToBuffer(nodes) {
    const encoder = new TextEncoder();
    let totalSize = 4;
    
    nodes.forEach(node => {
        const idBytes = encoder.encode(node.id);
        totalSize += 1 + idBytes.length + 8;
    });
    
    const buffer = new ArrayBuffer(totalSize);
    const view = new DataView(buffer);
    let offset = 0;
    
    view.setUint32(offset, nodes.length, true);
    offset += 4;
    
    nodes.forEach(node => {
        const idBytes = encoder.encode(node.id);
        view.setUint8(offset, idBytes.length);
        offset++;
        new Uint8Array(buffer, offset, idBytes.length).set(idBytes);
        offset += idBytes.length;
        view.setFloat32(offset, node.x, true);
        offset += 4;
        view.setFloat32(offset, node.y, true);
        offset += 4;
    });
    
    return buffer;
}

/**
 * 序列化边为 ArrayBuffer
 */
function serializeLinksToBuffer(links, nodes) {
    const totalSize = 4 + links.length * 8;
    const buffer = new ArrayBuffer(totalSize);
    const view = new DataView(buffer);
    let offset = 0;
    
    view.setUint32(offset, links.length, true);
    offset += 4;
    
    links.forEach(link => {
        const srcIdx = nodes.findIndex(n => n.id === link.source);
        const tgtIdx = nodes.findIndex(n => n.id === link.target);
        view.setUint16(offset, srcIdx, true);
        offset += 2;
        view.setUint16(offset, tgtIdx, true);
        offset += 2;
        view.setFloat32(offset, link.value, true);
        offset += 4;
    });
    
    return buffer;
}

/**
 * 从 ArrayBuffer 读取边数据
 */
function parseEdges(buffer, nodes) {
    const view = new DataView(buffer);
    const edgeCount = view.getUint32(0, true);
    const edges = [];
    
    let offset = 4;
    for (let i = 0; i < edgeCount; i++) {
        const srcIdx = view.getUint16(offset, true);
        offset += 2;
        const tgtIdx = view.getUint16(offset, true);
        offset += 2;
        const value = view.getFloat32(offset, true);
        offset += 4;
        
        edges.push({
            id: i,
            source: nodes[srcIdx].id,
            target: nodes[tgtIdx].id,
            srcIdx,
            tgtIdx,
            value,
            controlPoints: []
        });
    }
    
    return edges;
}

/**
 * 将控制点序列化为 ArrayBuffer (transferable)
 */
function serializeControlPoints(edges) {
    let totalPoints = 0;
    for (const edge of edges) {
        totalPoints += edge.controlPoints.length;
    }
    
    // 布局：[edgeId, pointIndex, x, y, edgeId, pointIndex, x, y, ...]
    const byteSize = totalPoints * 16 + edges.length * 4; // 每个点 16 字节 + 每条边 4 字节 (偏移)
    const buffer = new ArrayBuffer(totalPoints * 16 + edges.length * 4);
    const view = new DataView(buffer);
    
    let offset = 0;
    let pointOffset = 0;
    
    for (const edge of edges) {
        view.setUint32(offset, edge.controlPoints.length, true);
        offset += 4;
        
        for (let i = 0; i < edge.controlPoints.length; i++) {
            const cp = edge.controlPoints[i];
            view.setFloat32(offset, cp.x, true);
            offset += 4;
            view.setFloat32(offset, cp.y, true);
            offset += 4;
        }
        pointOffset += edge.controlPoints.length;
    }
    
    perfStats.totalControlPoints = totalPoints;
    
    return { buffer, pointCount: totalPoints };
}

/**
 * 计算边兼容性 (优化版 - 使用索引访问)
 */
function computeCompatibility(e1, e2, nodes) {
    if (!e1.controlPoints || !e2.controlPoints || 
        e1.controlPoints.length === 0 || e2.controlPoints.length === 0) {
        return 0;
    }
    
    const cp1 = e1.controlPoints[0];
    const cp2 = e2.controlPoints[0];
    const angle1 = Math.atan2(cp1.y, cp1.x);
    const angle2 = Math.atan2(cp2.y, cp2.x);
    const angleComp = 1 - (Math.abs(angle1 - angle2) / Math.PI);
    
    const src1 = nodes[e1.srcIdx];
    const tgt1 = nodes[e1.tgtIdx];
    const src2 = nodes[e2.srcIdx];
    const tgt2 = nodes[e2.tgtIdx];
    
    const len1 = distance(src1.x, src1.y, tgt1.x, tgt1.y);
    const len2 = distance(src2.x, src2.y, tgt2.x, tgt2.y);
    const maxLen = Math.max(len1, len2, 1);
    const lenComp = 1 - Math.abs(len1 - len2) / maxLen;
    
    const srcDist = distance(src1.x, src1.y, src2.x, src2.y);
    const posComp = 1 / (1 + srcDist / 200);
    
    return (angleComp + lenComp + posComp) / 3;
}

// ==================== 核心算法 ====================

function initControlPoints(edges, nodes) {
    debugLog(`Initializing control points for ${edges.length} edges, divisions=${config.divisions}`);
    
    for (const edge of edges) {
        edge.controlPoints = [];
        const src = nodes[edge.srcIdx];
        const tgt = nodes[edge.tgtIdx];
        
        for (let i = 1; i < config.divisions; i++) {
            const t = i / config.divisions;
            edge.controlPoints.push({
                x: src.x + (tgt.x - src.x) * t,
                y: src.y + (tgt.y - src.y) * t
            });
        }
    }
    
    perfStats.totalControlPoints = edges.length * (config.divisions - 1);
}

function applyFDEB(edges, nodes, onProgress) {
    const springStrength = 0.05;
    const attractionStrength = config.bundlingStrength * 0.02;
    
    debugLog(`Starting FDEB: iterations=${config.iterations}, strength=${config.bundlingStrength}`);
    debugLog(`Total edges: ${edges.length}, control points: ${perfStats.totalControlPoints}`);
    
    const startTime = performance.now();
    
    for (let iter = 0; iter < config.iterations && !shouldStop; iter++) {
        const iterStart = performance.now();
        
        for (const edge of edges) {
            for (let i = 0; i < edge.controlPoints.length; i++) {
                const cp = edge.controlPoints[i];
                let fx = 0, fy = 0;
                
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
                
                for (const other of edges) {
                    if (edge === other || other.controlPoints.length <= i) continue;
                    
                    const compat = computeCompatibility(edge, other, nodes);
                    if (compat < config.compatibilityThreshold) continue;
                    
                    const ocp = other.controlPoints[i];
                    const dx = ocp.x - cp.x;
                    const dy = ocp.y - cp.y;
                    const dist = Math.hypot(dx, dy);
                    
                    if (dist > 0 && dist < 150) {
                        const force = attractionStrength * compat / dist;
                        fx += dx * force;
                        fy += dy * force;
                    }
                }
                
                cp.x += fx;
                cp.y += fy;
            }
        }
        
        const iterEnd = performance.now();
        const iterTime = (iterEnd - iterStart).toFixed(2);
        debugLog(`Iteration ${iter + 1}/${config.iterations}: ${iterTime}ms`);
        
        const progress = (iter + 1) / config.iterations * 100;
        if (onProgress) {
            onProgress(progress, edges);
        }
    }
    
    const endTime = performance.now();
    perfStats.computeTime = endTime - startTime;
    
    debugLog(`FDEB ${shouldStop ? 'stopped' : 'completed'} in ${perfStats.computeTime.toFixed(2)}ms`);
}

// ==================== 消息处理 ====================

self.onmessage = function(e) {
    const { type, data, transferables } = e.data;
    
    if (type === 'CONFIG') {
        if (data.bundlingStrength !== undefined) config.bundlingStrength = data.bundlingStrength;
        if (data.divisions !== undefined) config.divisions = data.divisions;
        if (data.iterations !== undefined) config.iterations = data.iterations;
        if (data.debug !== undefined) config.debug = data.debug;
        if (data.transferableThreshold !== undefined) config.transferableThreshold = data.transferableThreshold;
        if (data.autoMode !== undefined) config.autoMode = data.autoMode;
        
        debugLog('Config updated:', config);
        self.postMessage({ type: 'CONFIG_UPDATED', config });
        
    } else if (type === 'RUN_FDEB_HYBRID') {
        // 混合模式 - 根据数据量自动选择
        shouldStop = false;
        perfStats = { serializeTime: 0, computeTime: 0, transferTime: 0, totalEdges: 0, totalControlPoints: 0 };
        
        const { nodes, links, useTransferable } = data;
        
        debugLog(`Hybrid mode: ${useTransferable ? 'Transferable' : 'Standard'} (threshold=${config.transferableThreshold}, nodes=${nodes.length})`);
        
        const transferStart = performance.now();
        
        if (useTransferable) {
            // Transferable 模式
            const nodesBuffer = serializeNodesToBuffer(nodes);
            const edgesBuffer = serializeLinksToBuffer(links, nodes);
            const edges = parseEdges(edgesBuffer, parseNodes(nodesBuffer));
            const transferEnd = performance.now();
            
            perfStats.transferTime = transferEnd - transferStart;
            perfStats.totalEdges = edges.length;
            
            debugLog(`Transferable: ${nodes.length} nodes, ${edges.length} edges`);
            debugLog(`Transfer time: ${perfStats.transferTime.toFixed(2)}ms`);
            
            initControlPoints(edges, nodes);
            applyFDEB(edges, nodes, (progress, updatedEdges) => {
                if (Math.round(progress) % 10 === 0 || progress >= 100) {
                    const { buffer, pointCount } = serializeControlPoints(updatedEdges);
                    self.postMessage({
                        type: 'PROGRESS',
                        progress,
                        controlPointsBuffer: buffer,
                        pointCount,
                        edgeCount: updatedEdges.length,
                        mode: 'transferable'
                    }, [buffer]);
                }
            });
            
            if (!shouldStop) {
                const { buffer, pointCount } = serializeControlPoints(edges);
                self.postMessage({
                    type: 'COMPLETE',
                    controlPointsBuffer: buffer,
                    pointCount,
                    edgeCount: edges.length,
                    perfStats,
                    mode: 'transferable'
                }, [buffer]);
            } else {
                self.postMessage({ type: 'STOPPED', mode: 'transferable' });
            }
        } else {
            // 标准模式
            const edges = links.map((link, idx) => ({
                id: idx,
                source: link.source,
                target: link.target,
                srcIdx: nodes.findIndex(n => n.id === link.source),
                tgtIdx: nodes.findIndex(n => n.id === link.target),
                value: link.value,
                controlPoints: []
            }));
            
            const transferEnd = performance.now();
            perfStats.transferTime = transferEnd - transferStart;
            perfStats.totalEdges = edges.length;
            
            debugLog(`Standard: ${nodes.length} nodes, ${edges.length} edges`);
            debugLog(`Transfer time: ${perfStats.transferTime.toFixed(2)}ms (structured clone)`);
            
            initControlPoints(edges, nodes);
            
            applyFDEB(edges, nodes, (progress, updatedEdges) => {
                if (Math.round(progress) % 10 === 0 || progress >= 100) {
                    self.postMessage({ type: 'PROGRESS', progress, edges: updatedEdges, mode: 'standard' });
                }
            });
            
            if (!shouldStop) {
                self.postMessage({ type: 'COMPLETE', edges, perfStats, mode: 'standard' });
            } else {
                self.postMessage({ type: 'STOPPED', mode: 'standard' });
            }
        }
        
    } else if (type === 'RUN_FDEB_TRANSFERABLE') {
        // Transferable 模式
        shouldStop = false;
        perfStats = { serializeTime: 0, computeTime: 0, transferTime: 0, totalEdges: 0, totalControlPoints: 0 };
        
        const transferStart = performance.now();
        const nodes = parseNodes(data.nodesBuffer);
        const edges = parseEdges(data.edgesBuffer, nodes);
        const transferEnd = performance.now();
        
        perfStats.transferTime = transferEnd - transferStart;
        perfStats.totalEdges = edges.length;
        
        debugLog(`Received ${nodes.length} nodes, ${edges.length} edges via transferable`);
        debugLog(`Transfer time: ${perfStats.transferTime.toFixed(2)}ms`);
        
        // 释放原始 buffer (已转移所有权)
        if (data.nodesBuffer) data.nodesBuffer = null;
        if (data.edgesBuffer) data.edgesBuffer = null;
        
        initControlPoints(edges, nodes);
        
        applyFDEB(edges, nodes, (progress, updatedEdges) => {
            if (Math.round(progress) % 10 === 0 || progress >= 100) {
                const { buffer, pointCount } = serializeControlPoints(updatedEdges);
                self.postMessage({
                    type: 'PROGRESS',
                    progress,
                    controlPointsBuffer: buffer,
                    pointCount,
                    edgeCount: updatedEdges.length
                }, [buffer]);
            }
        });
        
        if (!shouldStop) {
            const { buffer, pointCount } = serializeControlPoints(edges);
            self.postMessage({
                type: 'COMPLETE',
                controlPointsBuffer: buffer,
                pointCount,
                edgeCount: edges.length,
                perfStats
            }, [buffer]);
        } else {
            self.postMessage({ type: 'STOPPED' });
        }
        
    } else if (type === 'RUN_FDEB') {
        // 传统模式 (向后兼容)
        shouldStop = false;
        const { nodes, links } = data;
        
        const edges = links.map((link, idx) => ({
            id: idx,
            source: link.source,
            target: link.target,
            srcIdx: nodes.findIndex(n => n.id === link.source),
            tgtIdx: nodes.findIndex(n => n.id === link.target),
            value: link.value,
            controlPoints: []
        }));
        
        initControlPoints(edges, nodes);
        
        applyFDEB(edges, nodes, (progress, updatedEdges) => {
            if (Math.round(progress) % 10 === 0 || progress >= 100) {
                self.postMessage({ type: 'PROGRESS', progress, edges: updatedEdges });
            }
        });
        
        if (!shouldStop) {
            self.postMessage({ type: 'COMPLETE', edges });
        } else {
            self.postMessage({ type: 'STOPPED' });
        }
        
    } else if (type === 'STOP') {
        shouldStop = true;
        debugLog('Stop requested');
        
    } else if (type === 'DEBUG') {
        config.debug = data.enabled;
        debugLog(`Debug mode ${config.debug ? 'enabled' : 'disabled'}`);
        
    } else if (type === 'GET_STATS') {
        self.postMessage({ type: 'STATS', stats: perfStats });
    }
};

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

debugLog('FDEB Worker (Transferable v2.0) initialized');
self.postMessage({ type: 'READY', version: '2.0-transferable' });
