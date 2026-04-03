// ==UserScript==
// @name         塑价通 · 期货价格自动识别
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  自动识别网页上的塑料期货价格（PE/PP/PVC），一键填入塑价通
// @match        https://*.eastmoney.com/*
// @match        https://*.dce.com.cn/*
// @match        https://*.sinock.com.cn/*
// @grant        none
// @run-at       document_idle
// ==/UserScript==

(function() {
  'use strict';

  const SUJIATONG_URL = 'https://material-price-tracker.vercel.app';

  // 关键词对应的期货品种
  const KEYWORDS = {
    pe: ['LLDPE', '线性低密度聚乙烯', '聚乙烯', 'PE(', '塑料 PE', 'PE 期货'],
    pp: ['PP(', '聚丙烯', 'PP 拉丝', 'PP期货', '塑料 PP'],
    pvc: ['PVC(', '聚氯乙烯', 'PVC 期货', '塑料 PVC']
  };

  function findPrices() {
    const results = { pe: null, pp: null, pvc: null };

    // 方案1：从表格中找（东方财富等行情表格）
    const cells = document.querySelectorAll('td, .cell, .price, [class*="price"]');
    for (const cell of cells) {
      const text = cell.innerText;
      for (const [type, kws] of Object.entries(KEYWORDS)) {
        for (const kw of kws) {
          if (text.includes(kw) || cell.innerHTML.includes(kw)) {
            const match = text.match(/\d{3,5}(?:[,,]\d{3})*/);
            if (match && !results[type]) {
              const num = parseInt(match[0].replace(/[,，]/g, ''));
              if (num > 5000 && num < 20000) {
                results[type] = num;
              }
            }
          }
        }
      }
    }

    // 方案2：从数字+关键词组合找
    if (!results.pe || !results.pp || !results.pvc) {
      const allText = document.body.innerText;
      if (!results.pe) { const m = allText.match(/PE[^\d]*(\d{4,5})/); if (m) results.pe = parseInt(m[1]); }
      if (!results.pp) { const m = allText.match(/PP[^\d]*(\d{4,5})/); if (m) results.pp = parseInt(m[1]); }
      if (!results.pvc) { const m = allText.match(/PVC[^\d]*(\d{4,5})/); if (m) results.pvc = parseInt(m[1]); }
    }

    // 方案3：大数字法（找最大的几个价格数字）
    const allNumbers = allText.match(/\d{4,5}/g) || [];
    const validPrices = [...new Set(allNumbers.map(n => parseInt(n))).values()]
      .filter(n => n >= 6000 && n <= 12000)
      .sort((a, b) => b - a);

    if (validPrices.length >= 1 && !results.pe) results.pe = validPrices[0];
    if (validPrices.length >= 2 && !results.pp) results.pp = validPrices[1];
    if (validPrices.length >= 3 && !results.pvc) results.pvc = validPrices[2];

    return results;
  }

  function createUI() {
    const prices = findPrices();
    const found = Object.entries(prices).filter(([,v]) => v).length;

    const div = document.createElement('div');
    div.id = 'sujiatong-float';
    div.innerHTML = `
      <style>
        #sujiatong-float {
          position: fixed; bottom: 20px; right: 20px; z-index: 999999;
          background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);
          padding: 14px 16px; font-family: -apple-system, "PingFang SC", sans-serif;
          min-width: 200px; max-width: 280px;
        }
        #sujiatong-float .title {
          font-size: 14px; font-weight: bold; color: #2196F3; margin-bottom: 8px;
          display: flex; justify-content: space-between; align-items: center;
        }
        #sujiatong-float .title .badge {
          font-size: 11px; background: #e3f2fd; color: #1976D2;
          padding: 2px 6px; border-radius: 4px; font-weight: normal;
        }
        #sujiatong-float .row {
          display: flex; justify-content: space-between; padding: 4px 0;
          font-size: 13px; border-bottom: 1px solid #f0f0f0;
        }
        #sujiatong-float .row:last-of-type { border-bottom: none; }
        #sujiatong-float .label { color: #666; }
        #sujiatong-float .val { font-weight: bold; color: #333; }
        #sujiatong-float .val.up { color: #e74c3c; }
        #sujiatong-float .val.down { color: #27ae60; }
        #sujiatong-float .found { font-size: 11px; color: #999; margin-top: 6px; }
        #sujiatong-float .btn {
          display: block; width: 100%; margin-top: 10px; padding: 8px;
          background: #2196F3; color: white; border: none; border-radius: 6px;
          font-size: 13px; cursor: pointer; text-align: center; text-decoration: none;
        }
        #sujiatong-float .btn:hover { background: #1976D2; }
        #sujiatong-float .close {
          background: none; border: none; cursor: pointer; font-size: 16px;
          color: #999; padding: 0; line-height: 1;
        }
        #sujiatong-float .close:hover { color: #666; }
      </style>
      <div class="title">
        <span>塑价通</span>
        <div>
          <span class="badge">${found > 0 ? '检测到' + found + '个价格' : '未检测到价格'}</span>
          <button class="close" onclick="document.getElementById('sujiatong-float').remove()">×</button>
        </div>
      </div>
      <div class="row"><span class="label">PE</span><span class="val ${prices.pe ? 'up' : ''}">${prices.pe || '—'}</span></div>
      <div class="row"><span class="label">PP</span><span class="val ${prices.pp ? 'up' : ''}">${prices.pp || '—'}</span></div>
      <div class="row"><span class="label">PVC</span><span class="val ${prices.pvc ? 'up' : ''}">${prices.pvc || '—'}</span></div>
      <div class="found">${found > 0 ? '价格已识别，可发送到塑价通' : '在行情页面自动检测'}</div>
      ${found > 0 ? '<a class="btn" href="' + SUJIATONG_URL + '?pe=' + (prices.pe||'') + '&pp=' + (prices.pp||'') + '&pvc=' + (prices.pvc||'') + '" target="_blank">打开塑价通并填入 →</a>' : ''}
    `;
    document.body.appendChild(div);
  }

  // 延迟加载，避免影响页面
  if (document.readyState === 'complete') {
    setTimeout(createUI, 1000);
  } else {
    window.addEventListener('load', () => setTimeout(createUI, 1000));
  }
})();
