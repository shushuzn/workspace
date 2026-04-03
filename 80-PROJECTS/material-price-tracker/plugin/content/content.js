// 内容脚本：识别页面上的期货价格
(function() {
  // 价格正则：匹配 "8500" "8500元" "8,500" 等常见格式
  const PRICE_RE = /(\d{3,5}(?:[,，]\d{3})*(?:\.\d+)?)\s*(?:元|¥|RMB)?\s*(?:\/?\s*吨)?/g;

  // 关键词对应的期货品种
  const KEYWORDS = {
    pe: ['LLDPE', '线性低密度聚乙烯', '聚乙烯', 'PE(", '塑料 PE', 'PE 期货'],
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
            const match = text.match(/\d{3,5}(?:[,，]\d{3})*/);
            if (match && !results[type]) {
              const num = parseInt(match[0].replace(/[,，]/g, ''));
              if (num > 5000 && num < 20000) { // 塑料期货合理范围
                results[type] = num;
              }
            }
          }
        }
      }
    }

    // 方案2：从数字+关键词组合找（更宽泛）
    if (!results.pe || !results.pp || !results.pvc) {
      const allText = document.body.innerText;
      // 找PE相关数字
      if (!results.pe) {
        const peMatch = allText.match(/PE[^\d]*(\d{4,5})/);
        if (peMatch) results.pe = parseInt(peMatch[1]);
      }
      if (!results.pp) {
        const ppMatch = allText.match(/PP[^\d]*(\d{4,5})/);
        if (ppMatch) results.pp = parseInt(ppMatch[1]);
      }
      if (!results.pvc) {
        const pvcMatch = allText.match(/PVC[^\d]*(\d{4,5})/);
        if (pvcMatch) results.pvc = parseInt(pvcMatch[1]);
      }
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

  // 监听来自 popup 的消息
  chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === 'GET_PRICES') {
      const prices = findPrices();
      sendResponse(prices);
    }
    return true;
  });

  // 页面加载后自动检测
  window._sjtPrices = findPrices();
  console.log('[塑价通插件] 检测到价格:', window._sjtPrices);
})();
