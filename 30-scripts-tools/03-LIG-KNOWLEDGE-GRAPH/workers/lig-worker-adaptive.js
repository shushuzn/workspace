/**
 * LIG Knowledge Graph - FDEB Worker (自适应阈值版)
 * 
 * 特性:
 * - 性能基准测试
 * - 动态阈值计算
 * - 历史数据学习
 * 
 * @version 3.0.0 (Adaptive)
 */

let config = {
    bundlingStrength: 0.6,
    divisions: 5,
    iterations: 15,
    compatibilityThreshold: 0.5,
    debug: false,
    autoMode: true,
    transferableThreshold: 50,
    adaptiveThreshold: true,
    minThreshold: 20,
    maxThreshold: 200
};

let shouldStop = false;
let perfStats = {
    serializeTime: 0,
    computeTime: 0,
    transferTime: 0,
    totalTime: 0,
    totalEdges: 0,
    totalControlPoints: 0,
    benchmarkResults: []
};

// 性能样本 (用于自适应阈值计算)
let performanceSamples = [];

function debugLog(...args) {
    if (config.debug) console.log('[FDEB Worker]', ...args);
}

function distance(x1, y1, x2, y2) {
    return Math.hypot(x2 - x1, y2 - y1);
}

function parseNodes(buffer) {
    const view = new DataView(buffer);
    const nodeCount = view.getUint32(0, true);
    const nodes = [];
    let offset = 4;
    for (let i = 0; i < nodeCount; i++) {
        const idLen = view.getUint8(offset); offset++;
        const idBytes = new Uint8Array(buffer, offset, idLen);
        const id = new TextDecoder().decode(idBytes); offset += idLen;
        const x = view.getFloat32(offset, true); offset += 4;
        const y = view.getFloat32(offset, true); offset += 4;
        nodes.push({ id, x, y });
    }
    return nodes;
}

function parseEdges(buffer, nodes) {
    const view = new DataView(buffer);
    const edgeCount = view.getUint32(0, true);
    const edges = [];
    let offset = 4;
    for (let i = 0; i < edgeCount; i++) {
        const srcIdx = view.getUint16(offset, true); offset += 2;
        const tgtIdx = view.getUint16(offset, true); offset += 2;
        const value = view.getFloat32(offset, true); offset += 4;
        edges.push({ id: i, source: nodes[srcIdx].id, target: nodes[tgtIdx].id, srcIdx, tgtIdx, value, controlPoints: [] });
    }
    return edges;
}

function serializeNodesToBuffer(nodes) {
    const encoder = new TextEncoder();
    let size = 4;
    nodes.forEach(n => { const b = encoder.encode(n.id); size += 1 + b.length + 8; });
    const buffer = new ArrayBuffer(size);
    const view = new DataView(buffer);
    let offset = 0;
    view.setUint32(offset, nodes.length, true); offset += 4;
    nodes.forEach(n => {
        const b = encoder.encode(n.id);
        view.setUint8(offset, b.length); offset++;
        new Uint8Array(buffer, offset, b.length).set(b); offset += b.length;
        view.setFloat32(offset, n.x, true); offset += 4;
        view.setFloat32(offset, n.y, true); offset += 4;
    });
    return buffer;
}

function serializeLinksToBuffer(links, nodes) {
    const buffer = new ArrayBuffer(4 + links.length * 8);
    const view = new DataView(buffer);
    let offset = 4;
    view.setUint32(0, links.length, true);
    links.forEach(link => {
        const srcIdx = nodes.findIndex(n => n.id === link.source);
        const tgtIdx = nodes.findIndex(n => n.id === link.target);
        view.setUint16(offset, srcIdx, true); offset += 2;
        view.setUint16(offset, tgtIdx, true); offset += 2;
        view.setFloat32(offset, link.value, true); offset += 4;
    });
    return buffer;
}

function serializeControlPoints(edges) {
    let totalPoints = 0;
    edges.forEach(e => totalPoints += e.controlPoints.length);
    const buffer = new ArrayBuffer(edges.length * 4 + totalPoints * 8);
    const view = new DataView(buffer);
    let offset = 0;
    edges.forEach(edge => {
        view.setUint32(offset, edge.controlPoints.length, true); offset += 4;
        edge.controlPoints.forEach(cp => {
            view.setFloat32(offset, cp.x, true); offset += 4;
            view.setFloat32(offset, cp.y, true); offset += 4;
        });
    });
    return { buffer, pointCount: totalPoints };
}

function computeCompatibility(e1, e2, nodes) {
    if (!e1.controlPoints.length || !e2.controlPoints.length) return 0;
    const cp1 = e1.controlPoints[0], cp2 = e2.controlPoints[0];
    const angle1 = Math.atan2(cp1.y, cp1.x), angle2 = Math.atan2(cp2.y, cp2.x);
    const angleComp = 1 - (Math.abs(angle1 - angle2) / Math.PI);
    const src1 = nodes[e1.srcIdx], tgt1 = nodes[e1.tgtIdx];
    const src2 = nodes[e2.srcIdx], tgt2 = nodes[e2.tgtIdx];
    const len1 = distance(src1.x, src1.y, tgt1.x, tgt1.y);
    const len2 = distance(src2.x, src2.y, tgt2.x, tgt2.y);
    const lenComp = 1 - Math.abs(len1 - len2) / Math.max(len1, len2, 1);
    const srcDist = distance(src1.x, src1.y, src2.x, src2.y);
    const posComp = 1 / (1 + srcDist / 200);
    return (angleComp + lenComp + posComp) / 3;
}

function initControlPoints(edges, nodes) {
    edges.forEach(edge => {
        edge.controlPoints = [];
        const src = nodes[edge.srcIdx], tgt = nodes[edge.tgtIdx];
        for (let i = 1; i < config.divisions; i++) {
            const t = i / config.divisions;
            edge.controlPoints.push({ x: src.x + (tgt.x - src.x) * t, y: src.y + (tgt.y - src.y) * t });
        }
    });
}

function applyFDEB(edges, nodes, onProgress) {
    const springStrength = 0.05;
    const attractionStrength = config.bundlingStrength * 0.02;
    const startTime = performance.now();
    
    for (let iter = 0; iter < config.iterations && !shouldStop; iter++) {
        for (const edge of edges) {
            for (let i = 0; i < edge.controlPoints.length; i++) {
                const cp = edge.controlPoints[i];
                let fx = 0, fy = 0;
                if (i > 0) { fx += (edge.controlPoints[i-1].x - cp.x) * springStrength; fy += (edge.controlPoints[i-1].y - cp.y) * springStrength; }
                if (i < edge.controlPoints.length - 1) { fx += (edge.controlPoints[i+1].x - cp.x) * springStrength; fy += (edge.controlPoints[i+1].y - cp.y) * springStrength; }
                for (const other of edges) {
                    if (edge === other || other.controlPoints.length <= i) continue;
                    const compat = computeCompatibility(edge, other, nodes);
                    if (compat < config.compatibilityThreshold) continue;
                    const ocp = other.controlPoints[i];
                    const dx = ocp.x - cp.x, dy = ocp.y - cp.y, dist = Math.hypot(dx, dy);
                    if (dist > 0 && dist < 150) { const f = attractionStrength * compat / dist; fx += dx * f; fy += dy * f; }
                }
                cp.x += fx; cp.y += fy;
            }
        }
        if (onProgress && Math.round((iter+1)/config.iterations*100) % 10 === 0) {
            onProgress((iter + 1) / config.iterations * 100, edges);
        }
    }
    
    perfStats.computeTime = performance.now() - startTime;
}

/**
 * 运行性能基准测试
 */
function runBenchmark(nodes, links) {
    const results = { nodeCount: nodes.length, edgeCount: links.length };
    
    // 测试 Standard 模式
    const stdStart = performance.now();
    const stdEdges = links.map((link, idx) => ({
        id: idx, source: link.source, target: link.target,
        srcIdx: nodes.findIndex(n => n.id === link.source),
        tgtIdx: nodes.findIndex(n => n.id === link.target),
        value: link.value, controlPoints: []
    }));
    initControlPoints(stdEdges, nodes);
    const stdEnd = performance.now();
    results.standardTime = stdEnd - stdStart;
    
    // 测试 Transferable 模式 (序列化开销)
    const transStart = performance.now();
    const nodesBuffer = serializeNodesToBuffer(nodes);
    const edgesBuffer = serializeLinksToBuffer(links, nodes);
    const transEnd = performance.now();
    results.transferableTime = transEnd - transStart;
    
    // 计算最优阈值
    const timeDiff = results.transferableTime - results.standardTime;
    results.recommended = timeDiff > 0 ? 'Standard' : 'Transferable';
    results.crossoverPoint = estimateCrossoverPoint(results);
    
    debugLog('Benchmark results:', results);
    
    return results;
}

/**
 * 估算交叉点 (最优阈值)
 * 基于线性回归：T(n) = a*n + b, S(n) = c*n + d
 * 交叉点：n = (d-b)/(a-c)
 */
function estimateCrossoverPoint(currentResult) {
    performanceSamples.push({
        n: currentResult.nodeCount,
        stdTime: currentResult.standardTime,
        transTime: currentResult.transferableTime
    });
    
    if (performanceSamples.length < 3) {
        return config.transferableThreshold;
    }
    
    // 简化：取最近 5 次样本的平均值
    const recent = performanceSamples.slice(-5);
    const avgStdTime = recent.reduce((s,x) => s + x.stdTime, 0) / recent.length;
    const avgTransTime = recent.reduce((s,x) => s + x.transTime, 0) / recent.length;
    const avgN = recent.reduce((s,x) => s + x.n, 0) / recent.length;
    
    // 估算斜率 (假设线性关系)
    const stdSlope = avgStdTime / avgN;
    const transSlope = avgTransTime / avgN;
    
    // 交叉点计算
    if (Math.abs(stdSlope - transSlope) < 0.001) return 50;
    
    const crossover = Math.round((avgTransTime - avgStdTime) / (stdSlope - transSlope));
    return Math.max(config.minThreshold, Math.min(config.maxThreshold, crossover));
}

/**
 * 动态调整阈值
 */
function adaptThreshold(benchmarkResult) {
    if (!config.adaptiveThreshold) return;
    
    const newThreshold = estimateCrossoverPoint(benchmarkResult);
    const oldThreshold = config.transferableThreshold;
    
    // 平滑更新 (避免剧烈波动)
    config.transferableThreshold = Math.round(oldThreshold * 0.7 + newThreshold * 0.3);
    
    debugLog(`Threshold adapted: ${oldThreshold} → ${config.transferableThreshold}`);
    
    return { old: oldThreshold, new: config.transferableThreshold, samples: performanceSamples.length };
}

self.onmessage = function(e) {
    const { type, data } = e.data;
    
    if (type === 'CONFIG') {
        if (data.bundlingStrength !== undefined) config.bundlingStrength = data.bundlingStrength;
        if (data.divisions !== undefined) config.divisions = data.divisions;
        if (data.iterations !== undefined) config.iterations = data.iterations;
        if (data.debug !== undefined) config.debug = data.debug;
        if (data.autoMode !== undefined) config.autoMode = data.autoMode;
        if (data.transferableThreshold !== undefined) config.transferableThreshold = data.transferableThreshold;
        if (data.adaptiveThreshold !== undefined) config.adaptiveThreshold = data.adaptiveThreshold;
        if (data.minThreshold !== undefined) config.minThreshold = data.minThreshold;
        if (data.maxThreshold !== undefined) config.maxThreshold = data.maxThreshold;
        
        self.postMessage({ type: 'CONFIG_UPDATED', config: {...config, samples: performanceSamples.length} });
        
    } else if (type === 'RUN_BENCHMARK') {
        const { nodes, links } = data;
        const results = runBenchmark(nodes, links);
        const adaptation = adaptThreshold(results);
        self.postMessage({ 
            type: 'BENCHMARK_COMPLETE', 
            results, 
            adaptation,
            threshold: config.transferableThreshold,
            samples: performanceSamples
        }, performanceSamples.map(s => s.nodesBuffer).filter(Boolean));
        
    } else if (type === 'RUN_FDEB_HYBRID') {
        shouldStop = false;
        perfStats = { serializeTime: 0, computeTime: 0, transferTime: 0, totalTime: 0, totalEdges: 0, totalControlPoints: 0, benchmarkResults: [] };
        const { nodes, links, useTransferable } = data;
        const startTime = performance.now();
        
        if (useTransferable) {
            const transferStart = performance.now();
            const nodesBuffer = serializeNodesToBuffer(nodes);
            const edgesBuffer = serializeLinksToBuffer(links, nodes);
            const edges = parseEdges(edgesBuffer, parseNodes(nodesBuffer));
            perfStats.transferTime = performance.now() - transferStart;
            perfStats.totalEdges = edges.length;
            initControlPoints(edges, nodes);
            applyFDEB(edges, nodes, (progress, edges) => {
                if (Math.round(progress) % 10 === 0) {
                    const { buffer, pointCount } = serializeControlPoints(edges);
                    self.postMessage({ type: 'PROGRESS', progress, controlPointsBuffer: buffer, pointCount, edgeCount: edges.length, mode: 'transferable' }, [buffer]);
                }
            });
            if (!shouldStop) {
                const { buffer, pointCount } = serializeControlPoints(edges);
                perfStats.totalTime = performance.now() - startTime;
                self.postMessage({ type: 'COMPLETE', controlPointsBuffer: buffer, pointCount, edgeCount: edges.length, perfStats, mode: 'transferable' }, [buffer]);
            } else {
                self.postMessage({ type: 'STOPPED', mode: 'transferable' });
            }
        } else {
            const edges = links.map((link, idx) => ({
                id: idx, source: link.source, target: link.target,
                srcIdx: nodes.findIndex(n => n.id === link.source),
                tgtIdx: nodes.findIndex(n => n.id === link.target),
                value: link.value, controlPoints: []
            }));
            perfStats.transferTime = performance.now() - startTime;
            perfStats.totalEdges = edges.length;
            initControlPoints(edges, nodes);
            applyFDEB(edges, nodes, (progress, edges) => {
                if (Math.round(progress) % 10 === 0) {
                    self.postMessage({ type: 'PROGRESS', progress, edges, mode: 'standard' });
                }
            });
            if (!shouldStop) {
                perfStats.totalTime = performance.now() - startTime;
                self.postMessage({ type: 'COMPLETE', edges, perfStats, mode: 'standard' });
            } else {
                self.postMessage({ type: 'STOPPED', mode: 'standard' });
            }
        }
        
    } else if (type === 'GET_SAMPLES') {
        self.postMessage({ type: 'SAMPLES', samples: performanceSamples, threshold: config.transferableThreshold });
    } else if (type === 'STOP') {
        shouldStop = true;
    } else if (type === 'DEBUG') {
        config.debug = data.enabled;
    } else if (type === 'RESET_SAMPLES') {
        performanceSamples = [];
        self.postMessage({ type: 'SAMPLES_RESET' });
    }
};

self.onerror = function(error) {
    self.postMessage({ type: 'ERROR', message: error.message });
};

debugLog('FDEB Worker (Adaptive v3.0) initialized');
self.postMessage({ type: 'READY', version: '3.0-adaptive', threshold: config.transferableThreshold });
