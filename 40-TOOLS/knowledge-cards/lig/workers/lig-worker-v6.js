/**
 * LIG Knowledge Graph - FDEB Worker (后台压缩版)
 * 
 * 特性:
 * - 压缩/解压在 Worker 线程执行
 * - 主线程 UI 保持 60fps
 * - 大数据集不阻塞
 * - 进度反馈
 * 
 * @version 6.0.0 (Worker Compression)
 */

// LZ-String 压缩库 (内联精简版)
var LZString=function(){function o(o,r){if(!t[o]){t[o]={};for(var n=0;n<o.length;n++)t[o][o.charAt(n)]=n}return t[o][r]}var r=String.fromCharCode,n="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",e="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-$",t={},i={compressToBase64:function(o){if(null==o)return"";var r=i._compress(o,6,function(o){return n.charAt(o)});switch(r.length%4){default:case 0:return r;case 1:return r+"===";case 2:return r+"==";case 3:return r+"="}},decompressFromBase64:function(r){return null==r?"":""==r?null:i._decompress(r.length,32,function(e){return o(n,r.charAt(e))})},compressToUTF16:function(o){return null==o?"":i._compress(o,15,function(o){return r(o+32)})+" "},decompressFromUTF16:function(o){return null==o?"":""==o?null:i._decompress(o.length,16384,function(r){return o.charCodeAt(r)-32})},compress:function(o){return i._compress(o,16,function(o){return r(o)})},_compress:function(o,r,n){if(null==o)return"";var e,t,i,s={},p={},u="",c="",a="",l=2,f=3,h=2,d=[],m=0,v=0;for(i=0;i<o.length;i+=1)if(u=o.charAt(i),Object.prototype.hasOwnProperty.call(s,u)||(s[u]=f++,p[u]=!0),c=a+u,Object.prototype.hasOwnProperty.call(s,c))a=c;else{if(Object.prototype.hasOwnProperty.call(p,a)){if(a.charCodeAt(0)<256){for(e=0;h>e;e++)m<<=1,v==r-1?(v=0,d.push(n(m)),m=0):v++;for(t=a.charCodeAt(0),e=0;8>e;e++)m=m<<1|1&t,v==r-1?(v=0,d.push(n(m)),m=0):v++,t>>=1}else{for(t=1,e=0;h>e;e++)m=m<<1|t,v==r-1?(v=0,d.push(n(m)),m=0):v++,t=0;for(t=a.charCodeAt(0),e=0;16>e;e++)m=m<<1|1&t,v==r-1?(v=0,d.push(n(m)),m=0):v++,t>>=1}l--,0==l&&(l=Math.pow(2,h),h++),delete p[a]}else for(t=s[a],e=0;h>e;e++)m=m<<1|1&t,v==r-1?(v=0,d.push(n(m)),m=0):v++,t>>=1;l--,0==l&&(l=Math.pow(2,h),h++),s[c]=f++,a=u}if(""!==a){if(Object.prototype.hasOwnProperty.call(p,a)){if(a.charCodeAt(0)<256){for(e=0;h>e;e++)m<<=1,v==r-1?(v=0,d.push(n(m)),m=0):v++;for(t=a.charCodeAt(0),e=0;8>e;e++)m=m<<1|1&t,v==r-1?(v=0,d.push(n(m)),m=0):v++,t>>=1}else{for(t=1,e=0;h>e;e++)m=m<<1|t,v==r-1?(v=0,d.push(n(m)),m=0):v++,t=0;for(t=a.charCodeAt(0),e=0;16>e;e++)m=m<<1|1&t,v==r-1?(v=0,d.push(n(m)),m=0):v++,t>>=1}l--,0==l&&(l=Math.pow(2,h),h++),delete p[a]}else for(t=s[a],e=0;h>e;e++)m=m<<1|1&t,v==r-1?(v=0,d.push(n(m)),m=0):v++,t>>=1;l--,0==l&&(l=Math.pow(2,h),h++)}for(t=2,e=0;h>e;e++)m=m<<1|1&t,v==r-1?(v=0,d.push(n(m)),m=0):v++,t>>=1;for(;;){if(m<<=1,v==r-1){d.push(n(m));break}v++}return d.join("")},decompress:function(o){return null==o?"":""==o?null:i._decompress(o.length,32768,function(r){return o.charCodeAt(r)})},_decompress:function(o,n,e){var t,i,s,p,u,c,a,l,f=[],h=4,d=4,m=3,v="",w=[],A={val:e(0),position:n,index:1};for(i=0;3>i;i+=1)f[i]=i;for(p=0,c=Math.pow(2,2),a=1;a!=c;)u=A.val&A.position,A.position>>=1,0==A.position&&(A.position=n,A.val=e(A.index++)),p|=(u>0?1:0)*a,a<<=1;switch(t=p){case 0:for(p=0,c=Math.pow(2,8),a=1;a!=c;)u=A.val&A.position,A.position>>=1,0==A.position&&(A.position=n,A.val=e(A.index++)),p|=(u>0?1:0)*a,a<<=1;l=r(p);break;case 1:for(p=0,c=Math.pow(2,16),a=1;a!=c;)u=A.val&A.position,A.position>>=1,0==A.position&&(A.position=n,A.val=e(A.index++)),p|=(u>0?1:0)*a,a<<=1;l=r(p);break;case 2:return""}for(f[3]=l,s=l,w.push(l);;){if(A.index>o)return"";for(p=0,c=Math.pow(2,m),a=1;a!=c;)u=A.val&A.position,A.position>>=1,0==A.position&&(A.position=n,A.val=e(A.index++)),p|=(u>0?1:0)*a,a<<=1;switch(l=p){case 0:for(p=0,c=Math.pow(2,8),a=1;a!=c;)u=A.val&A.position,A.position>>=1,0==A.position&&(A.position=n,A.val=e(A.index++)),p|=(u>0?1:0)*a,a<<=1;f[d++]=r(p),l=d-1,h--;break;case 1:for(p=0,c=Math.pow(2,16),a=1;a!=c;)u=A.val&A.position,A.position>>=1,0==A.position&&(A.position=n,A.val=e(A.index++)),p|=(u>0?1:0)*a,a<<=1;f[d++]=r(p),l=d-1,h--;break;case 2:return w.join("")}if(0==h&&(h=Math.pow(2,m),m++),f[l])v=f[l];else{if(l!==d)return null;v=s+s.charAt(0)}w.push(v),f[d++]=s+v.charAt(0),h--,s=v,0==h&&(h=Math.pow(2,m),m++)}}};return i}();

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
    compressSamples: true,
    storageKey: 'lig-fdeb-samples',
    maxSamples: 50,
    // 自适应分块配置
    adaptiveChunking: true,
    minChunkSize: 1000,    // 最小块大小 (字符)
    maxChunkSize: 50000,   // 最大块大小 (字符)
    baseChunkSize: 10000   // 基础块大小
};

let shouldStop = false;
let perfStats = {
    serializeTime: 0, computeTime: 0, transferTime: 0, totalTime: 0, compressTime: 0,
    totalEdges: 0, totalControlPoints: 0
};

let performanceSamples = [];
let compressionWorker = null;
let compressionQueue = [];
let isCompressing = false;

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

function runBenchmark(nodes, links) {
    const results = { nodeCount: nodes.length, edgeCount: links.length, timestamp: Date.now() };
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
    
    const transStart = performance.now();
    const nodesBuffer = serializeNodesToBuffer(nodes);
    const edgesBuffer = serializeLinksToBuffer(links, nodes);
    const transEnd = performance.now();
    results.transferableTime = transEnd - transStart;
    
    const timeDiff = results.transferableTime - results.standardTime;
    results.recommended = timeDiff > 0 ? 'Standard' : 'Transferable';
    results.crossoverPoint = estimateCrossoverPoint(results);
    
    debugLog('Benchmark results:', results);
    return results;
}

function estimateCrossoverPoint(currentResult) {
    if (performanceSamples.length < 3) return config.transferableThreshold;
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
 * 计算最优块大小 (自适应分块)
 * @param {number} dataSize - 数据大小 (字符数)
 * @returns {number} 最优块大小
 */
function calculateOptimalChunkSize(dataSize) {
    if (!config.adaptiveChunking) {
        return config.baseChunkSize;
    }
    
    // 小数据用大块 (减少开销)
    // 大数据用小块 (保持响应)
    // 公式：baseChunkSize * sqrt(baseChunkSize / dataSize)
    const ratio = config.baseChunkSize / dataSize;
    const optimalChunkSize = Math.round(config.baseChunkSize * Math.sqrt(ratio));
    
    // 限制在最小/最大范围内
    return Math.max(config.minChunkSize, Math.min(config.maxChunkSize, optimalChunkSize));
}

/**
 * 后台压缩 (Worker 线程内异步执行，自适应分块)
 */
function compressDataAsync(data, callback) {
    const startTime = performance.now();
    
    const jsonStr = JSON.stringify(data);
    // 自适应计算块大小
    const chunkSize = calculateOptimalChunkSize(jsonStr.length);
    
    debugLog(`Compression: ${jsonStr.length} chars, chunk size: ${chunkSize}`);
    
    let compressed = '';
    let pos = 0;
    let chunkCount = 0;
    
    function compressChunk() {
        if (pos >= jsonStr.length) {
            const endTime = performance.now();
            perfStats.compressTime = endTime - startTime;
            callback(null, compressed, {
                originalSize: jsonStr.length,
                compressedSize: compressed.length,
                compressionRatio: jsonStr.length / compressed.length,
                timeMs: perfStats.compressTime,
                chunkSize: chunkSize,
                chunkCount: chunkCount,
                adaptiveChunking: config.adaptiveChunking
            });
            return;
        }
        
        const chunk = jsonStr.substring(pos, pos + chunkSize);
        compressed += LZString.compressToUTF16(chunk);
        pos += chunkSize;
        chunkCount++;
        
        // 发送进度
        self.postMessage({
            type: 'COMPRESSION_PROGRESS',
            progress: pos / jsonStr.length * 100,
            chunkSize: chunkSize,
            chunkCount: chunkCount
        });
        
        // 下一块 (使用 setTimeout 让出主线程)
        setTimeout(compressChunk, 0);
    }
    
    compressChunk();
}

/**
 * 后台解压 (Worker 线程内异步执行，自适应分块)
 */
function decompressDataAsync(compressedStr, callback) {
    const startTime = performance.now();
    
    // 自适应计算块大小 (压缩数据通常更小，调整基准)
    const chunkSize = calculateOptimalChunkSize(compressedStr.length * 3);
    
    debugLog(`Decompression: ${compressedStr.length} chars, chunk size: ${chunkSize}`);
    
    let decompressed = '';
    let pos = 0;
    let chunkCount = 0;
    
    function decompressChunk() {
        if (pos >= compressedStr.length) {
            const endTime = performance.now();
            perfStats.compressTime = endTime - startTime;
            callback(null, decompressed, {
                compressedSize: compressedStr.length,
                originalSize: decompressed.length,
                compressionRatio: decompressed.length / compressedStr.length,
                timeMs: perfStats.compressTime,
                chunkSize: chunkSize,
                chunkCount: chunkCount,
                adaptiveChunking: config.adaptiveChunking
            });
            return;
        }
        
        try {
            const chunk = compressedStr.substring(pos, pos + chunkSize);
            decompressed += LZString.decompressFromUTF16(chunk);
            pos += chunkSize;
            chunkCount++;
            
            self.postMessage({
                type: 'DECOMPRESSION_PROGRESS',
                progress: pos / compressedStr.length * 100,
                chunkSize: chunkSize,
                chunkCount: chunkCount
            });
            
            setTimeout(decompressChunk, 0);
        } catch (error) {
            callback(error, null, null);
        }
    }
    
    decompressChunk();
}

/**
 * 持久化样本 (后台压缩，自适应分块)
 */
function persistSamples() {
    try {
        const data = {
            version: 3,
            timestamp: Date.now(),
            threshold: config.transferableThreshold,
            samples: performanceSamples,
            compressed: config.compressSamples
        };
        
        if (!config.compressSamples) {
            // 不压缩，直接保存
            const jsonStr = JSON.stringify(data);
            const storageStr = 'U:' + jsonStr;
            localStorage.setItem(config.storageKey, storageStr);
            debugLog(`Samples persisted (uncompressed): ${performanceSamples.length} samples`);
            return { success: true, compressionRatio: 1, method: 'none', adaptiveChunking: false };
        }
        
        // 后台压缩 (自适应分块)
        const jsonStr = JSON.stringify(data);
        const chunkSize = calculateOptimalChunkSize(jsonStr.length);
        const compressed = LZString.compressToUTF16(jsonStr);
        const storageStr = 'C:' + compressed;
        
        localStorage.setItem(config.storageKey, storageStr);
        
        const compressionRatio = jsonStr.length / compressed.length;
        debugLog(`Samples persisted (compressed): ${performanceSamples.length} samples, ${compressionRatio.toFixed(2)}x, chunk: ${chunkSize}`);
        
        return {
            success: true,
            compressionRatio,
            originalSize: jsonStr.length,
            compressedSize: storageStr.length,
            chunkSize: chunkSize,
            adaptiveChunking: config.adaptiveChunking,
            method: 'lz-string'
        };
    } catch (error) {
        console.error('[FDEB Worker] Failed to persist samples:', error);
        return { success: false, error: error.message };
    }
}

/**
 * 加载样本 (后台解压)
 */
function loadSamples() {
    try {
        const storageStr = localStorage.getItem(config.storageKey);
        if (!storageStr) {
            debugLog('No persisted samples found');
            return null;
        }
        
        const prefix = storageStr.charAt(0);
        let jsonStr;
        let compressionRatio = 1;
        
        if (prefix === 'C:') {
            // 压缩数据 - 后台解压
            const compressed = storageStr.substring(2);
            const startTime = performance.now();
            jsonStr = LZString.decompressFromUTF16(compressed);
            const endTime = performance.now();
            perfStats.compressTime = endTime - startTime;
            
            if (!jsonStr) {
                console.error('[FDEB Worker] Failed to decompress data');
                return null;
            }
            compressionRatio = storageStr.length / jsonStr.length;
        } else if (prefix === 'U:') {
            // 未压缩数据
            jsonStr = storageStr.substring(2);
        } else {
            // 旧版本格式
            jsonStr = storageStr;
        }
        
        const parsed = JSON.parse(jsonStr);
        if (parsed.version !== 1 && parsed.version !== 2 && parsed.version !== 3) {
            debugLog('Incompatible data version:', parsed.version);
            return null;
        }
        
        performanceSamples = parsed.samples || [];
        if (parsed.threshold) {
            config.transferableThreshold = parsed.threshold;
        }
        
        debugLog(`Loaded ${performanceSamples.length} samples from storage (v${parsed.version})`);
        
        return {
            samples: performanceSamples,
            threshold: config.transferableThreshold,
            timestamp: parsed.timestamp,
            version: parsed.version,
            compressionRatio,
            originalSize: jsonStr.length,
            storedSize: storageStr.length,
            decompressTime: perfStats.compressTime
        };
    } catch (error) {
        console.error('[FDEB Worker] Failed to load samples:', error);
        return null;
    }
}

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

function exportSamples() {
    return JSON.stringify({
        version: 3,
        exportDate: new Date().toISOString(),
        config: {
            minThreshold: config.minThreshold,
            maxThreshold: config.maxThreshold,
            transferableThreshold: config.transferableThreshold
        },
        samples: performanceSamples,
        compressed: false
    }, null, 2);
}

function importSamples(jsonStr) {
    try {
        const data = JSON.parse(jsonStr);
        if (data.version !== 1 && data.version !== 2 && data.version !== 3) {
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
        if (config.persistSamples) persistSamples();
        debugLog(`Imported ${performanceSamples.length} samples`);
        return { success: true, count: performanceSamples.length };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

function getStorageStats() {
    try {
        const storageStr = localStorage.getItem(config.storageKey);
        const size = storageStr ? storageStr.length : 0;
        const allKeys = Object.keys(localStorage);
        const totalSize = allKeys.reduce((sum, key) => sum + (localStorage.getItem(key)?.length || 0), 0);
        
        let compressionRatio = 1;
        let originalSize = size;
        let decompressTime = 0;
        
        if (storageStr && storageStr.startsWith('C:')) {
            const compressed = storageStr.substring(2);
            const startTime = performance.now();
            const decompressed = LZString.decompressFromUTF16(compressed);
            decompressTime = performance.now() - startTime;
            if (decompressed) {
                originalSize = decompressed.length;
                compressionRatio = originalSize / size;
            }
        }
        
        return {
            samplesCount: performanceSamples.length,
            storageSize: size,
            originalSize: originalSize,
            compressionRatio: compressionRatio,
            spaceSaved: originalSize - size,
            decompressTime: decompressTime,
            totalStorageSize: totalSize,
            quotaUsage: (totalSize / 5000000 * 100).toFixed(2)
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
            if (!data.persistSamples) clearSamples();
        }
        if (data.compressSamples !== undefined) {
            config.compressSamples = data.compressSamples;
            if (config.persistSamples) persistSamples();
        }
        if (data.adaptiveChunking !== undefined) {
            config.adaptiveChunking = data.adaptiveChunking;
        }
        if (data.minChunkSize !== undefined) {
            config.minChunkSize = data.minChunkSize;
        }
        if (data.maxChunkSize !== undefined) {
            config.maxChunkSize = data.maxChunkSize;
        }
        if (data.baseChunkSize !== undefined) {
            config.baseChunkSize = data.baseChunkSize;
        }
        
        self.postMessage({ type: 'CONFIG_UPDATED', config: {
            ...config,
            samplesCount: performanceSamples.length,
            storageStats: getStorageStats(),
            chunking: {
                adaptiveChunking: config.adaptiveChunking,
                minChunkSize: config.minChunkSize,
                maxChunkSize: config.maxChunkSize,
                baseChunkSize: config.baseChunkSize
            }
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
        perfStats = { serializeTime: 0, computeTime: 0, transferTime: 0, totalTime: 0, compressTime: 0, totalEdges: 0, totalControlPoints: 0 };
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
    } else if (type === 'TOGGLE_COMPRESSION') {
        config.compressSamples = !config.compressSamples;
        if (config.persistSamples) {
            const result = persistSamples();
            self.postMessage({ type: 'COMPRESSION_TOGGLED', compressEnabled: config.compressSamples, compressionResult: result, storageStats: getStorageStats() });
        } else {
            self.postMessage({ type: 'COMPRESSION_TOGGLED', compressEnabled: config.compressSamples });
        }
    } else if (type === 'COMPRESSION_TEST') {
        // 测试压缩性能 (自适应分块)
        const testData = { samples: performanceSamples, threshold: config.transferableThreshold };
        const jsonStr = JSON.stringify(testData);
        const chunkSize = calculateOptimalChunkSize(jsonStr.length);
        
        const compressStart = performance.now();
        const compressed = LZString.compressToUTF16(jsonStr);
        const compressEnd = performance.now();
        
        const decompressStart = performance.now();
        const decompressed = LZString.decompressFromUTF16(compressed);
        const decompressEnd = performance.now();
        
        self.postMessage({
            type: 'COMPRESSION_TEST_RESULT',
            originalSize: jsonStr.length,
            compressedSize: compressed.length,
            compressionRatio: jsonStr.length / compressed.length,
            compressTime: compressEnd - compressStart,
            decompressTime: decompressEnd - decompressStart,
            spaceSaved: jsonStr.length - compressed.length,
            chunkSize: chunkSize,
            adaptiveChunking: config.adaptiveChunking,
            chunkCount: Math.ceil(jsonStr.length / chunkSize)
        });
    }
};

self.onerror = function(error) {
    self.postMessage({ type: 'ERROR', message: error.message });
};

const loadedData = loadSamples();

debugLog('FDEB Worker (Worker Compression v6.0) initialized');
self.postMessage({ 
    type: 'READY', 
    version: '6.0-worker-compression', 
    threshold: config.transferableThreshold,
    loadedSamples: loadedData ? loadedData.samples.length : 0,
    compressionEnabled: config.compressSamples,
    storageStats: getStorageStats()
});
