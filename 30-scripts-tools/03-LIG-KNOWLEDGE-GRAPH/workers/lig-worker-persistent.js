/**
 * LIG Knowledge Graph - FDEB Worker (持久化版)
 * 
 * 特性:
 * - localStorage 持久化样本
 * - 样本导入/导出
 * - 存储状态管理
 * 
 * @version 4.0.0 (Persistent)
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
    maxThreshold: 200,
    persistSamples: true,
    storageKey: 'lig-fdeb-samples',
    maxSamples: 50
};

let shouldStop = false;
let perfStats = {
    serializeTime: 0, computeTime: 0, transferTime: 0, totalTime: 0,
    totalEdges: 0, totalControlPoints: 0
};

// 性能样本 (从 localStorage 加载)
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
    const results = { nodeCount: nodes.length, edgeCount: links.length, timestamp: Date.now() };
    
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
    
    // 测试 Transferable 模式
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
 * 估算交叉点
 */
function estimateCrossoverPoint(currentResult) {
    if (performanceSamples.length < 3) {
        return config.transferableThreshold;
    }
    
    const recent = performanceSamples.slice(-10);
    const avgStdTime = recent.reduce((s,x) => s + x.stdTime, 0) / recent.length;
    const avgTransTime = recent.reduce((s,x) => s + x.transTime, 0) / recent.length;
    const avgN = recent.reduce((s,x) => s + x.n, 0) / recent.length;
    
    const stdSlope = avgStdTime / avgN;
    const transSlope = avgTransTime / avgN;
    
    if (Math.abs(stdSlope - transSlope) < 0.001) return 50;
    
    const crossover = Math.round((avgTransTime - avgStdTime) / (stdSlope - transSlope));
    return Math.max(config.minThreshold, Math.min(config.maxThreshold, crossover));
}

/**
 * 动态调整阈值并持久化
 */
function adaptThreshold(benchmarkResult) {
    if (!config.adaptiveThreshold) return null;
    
    // 添加新样本
    performanceSamples.push({
        n: benchmarkResult.nodeCount,
        stdTime: benchmarkResult.standardTime,
        transTime: benchmarkResult.transferableTime,
        timestamp: benchmarkResult.timestamp
    });
    
    // 限制样本数量
    if (performanceSamples.length > config.maxSamples) {
        performanceSamples = performanceSamples.slice(-config.maxSamples);
    }
    
    // 持久化到 localStorage
    if (config.persistSamples) {
        persistSamples();
    }
    
    const newThreshold = estimateCrossoverPoint(benchmarkResult);
    const oldThreshold = config.transferableThreshold;
    
    // 平滑更新
    config.transferableThreshold = Math.round(oldThreshold * 0.7 + newThreshold * 0.3);
    
    debugLog(`Threshold adapted: ${oldThreshold} → ${config.transferableThreshold}`);
    
    return { old: oldThreshold, new: config.transferableThreshold, samples: performanceSamples.length };
}

/**
 * 持久化样本到 localStorage
 */
function persistSamples() {
    try {
        const data = {
            version: 1,
            timestamp: Date.now(),
            threshold: config.transferableThreshold,
            samples: performanceSamples
        };
        localStorage.setItem(config.storageKey, JSON.stringify(data));
        debugLog(`Samples persisted: ${performanceSamples.length} samples`);
        return true;
    } catch (error) {
        console.error('[FDEB Worker] Failed to persist samples:', error);
        return false;
    }
}

/**
 * 从 localStorage 加载样本
 */
function loadSamples() {
    try {
        const data = localStorage.getItem(config.storageKey);
        if (!data) {
            debugLog('No persisted samples found');
            return null;
        }
        
        const parsed = JSON.parse(data);
        if (parsed.version !== 1) {
            debugLog('Incompatible data version:', parsed.version);
            return null;
        }
        
        performanceSamples = parsed.samples || [];
        if (parsed.threshold) {
            config.transferableThreshold = parsed.threshold;
        }
        
        debugLog(`Loaded ${performanceSamples.length} samples from storage`);
        return {
            samples: performanceSamples,
            threshold: config.transferableThreshold,
            timestamp: parsed.timestamp
        };
    } catch (error) {
        console.error('[FDEB Worker] Failed to load samples:', error);
        return null;
    }
}

/**
 * 清除持久化样本
 */
function clearSamples() {
    try {
        localStorage.removeItem(config.storageKey);
        performanceSamples = [];
        debugLog('Samples cleared');
        return true;
    } catch (error) {
        console.error('[FDEB Worker] Failed to clear samples:', error);
        return false;
    }
}

/**
 * 导出样本为 JSON
 */
function exportSamples() {
    return JSON.stringify({
        version: 1,
        exportDate: new Date().toISOString(),
        config: {
            minThreshold: config.minThreshold,
            maxThreshold: config.maxThreshold,
            transferableThreshold: config.transferableThreshold
        },
        samples: performanceSamples
    }, null, 2);
}

/**
 * 导入样本
 */
function importSamples(jsonStr) {
    try {
        const data = JSON.parse(jsonStr);
        if (data.version !== 1) {
            return { success: false, error: 'Incompatible version' };
        }
        
        if (!Array.isArray(data.samples)) {
            return { success: false, error: 'Invalid samples format' };
        }
        
        performanceSamples = data.samples;
        if (data.config && data.config.transferableThreshold) {
            config.transferableThreshold = data.config.transferableThreshold;
        }
        if (data.config && data.config.minThreshold) {
            config.minThreshold = data.config.minThreshold;
        }
        if (data.config && data.config.maxThreshold) {
            config.maxThreshold = data.config.maxThreshold;
        }
        
        // 持久化导入的样本
        if (config.persistSamples) {
            persistSamples();
        }
        
        debugLog(`Imported ${performanceSamples.length} samples`);
        return { success: true, count: performanceSamples.length };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

/**
 * 获取存储状态
 */
function getStorageStats() {
    try {
        const data = localStorage.getItem(config.storageKey);
        const size = data ? data.length : 0;
        const allKeys = Object.keys(localStorage);
        const totalSize = allKeys.reduce((sum, key) => sum + (localStorage.getItem(key)?.length || 0), 0);
        
        return {
            samplesCount: performanceSamples.length,
            storageSize: size,
            totalStorageSize: totalSize,
            quotaUsage: (totalSize / 5000000 * 100).toFixed(2) // 假设 5MB quota
        };
    } catch (error) {
        return { error: error.message };
    }
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
        if (data.persistSamples !== undefined) {
            config.persistSamples = data.persistSamples;
            if (!data.persistSamples) {
                clearSamples();
            }
        }
        
        self.postMessage({ type: 'CONFIG_UPDATED', config: {
            ...config,
            samplesCount: performanceSamples.length,
            storageStats: getStorageStats()
        }});
        
    } else if (type === 'RUN_BENCHMARK') {
        const { nodes, links } = data;
        const results = runBenchmark(nodes, links);
        const adaptation = adaptThreshold(results);
        self.postMessage({ 
            type: 'BENCHMARK_COMPLETE', 
            results, 
            adaptation,
            threshold: config.transferableThreshold,
            samples: performanceSamples,
            storageStats: getStorageStats()
        });
        
    } else if (type === 'RUN_FDEB_HYBRID') {
        shouldStop = false;
        perfStats = { serializeTime: 0, computeTime: 0, transferTime: 0, totalTime: 0, totalEdges: 0, totalControlPoints: 0 };
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
        self.postMessage({ type: 'SAMPLES', samples: performanceSamples, threshold: config.transferableThreshold, storageStats: getStorageStats() });
    } else if (type === 'STOP') {
        shouldStop = true;
    } else if (type === 'DEBUG') {
        config.debug = data.enabled;
    } else if (type === 'RESET_SAMPLES') {
        clearSamples();
        self.postMessage({ type: 'SAMPLES_RESET', storageStats: getStorageStats() });
    } else if (type === 'EXPORT_SAMPLES') {
        const json = exportSamples();
        self.postMessage({ type: 'EXPORT_DATA', json });
    } else if (type === 'IMPORT_SAMPLES') {
        const result = importSamples(data.json);
        self.postMessage({ type: 'IMPORT_RESULT', ...result, storageStats: getStorageStats() });
    } else if (type === 'GET_STORAGE_STATS') {
        self.postMessage({ type: 'STORAGE_STATS', stats: getStorageStats() });
    } else if (type === 'LOAD_SAMPLES') {
        const loaded = loadSamples();
        self.postMessage({ type: 'SAMPLES_LOADED', loaded, samples: performanceSamples });
    }
};

self.onerror = function(error) {
    self.postMessage({ type: 'ERROR', message: error.message });
};

// 初始化时加载持久化样本
const loadedData = loadSamples();

debugLog('FDEB Worker (Persistent v4.0) initialized');
self.postMessage({ 
    type: 'READY', 
    version: '4.0-persistent', 
    threshold: config.transferableThreshold,
    loadedSamples: loadedData ? loadedData.samples.length : 0,
    storageStats: getStorageStats()
});
