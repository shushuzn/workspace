const SUJIATONG_URL = 'https://material-price-tracker.vercel.app';

// 从当前标签页获取检测到的价格
async function loadPrices() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  try {
    const result = await chrome.tabs.sendMessage(tab.id, { type: 'GET_PRICES' });
    if (result) {
      if (result.pe) {
        document.getElementById('pe-price').textContent = result.pe;
        document.getElementById('pe-price').className = 'value';
        document.getElementById('send-pe').value = result.pe;
      }
      if (result.pp) {
        document.getElementById('pp-price').textContent = result.pp;
        document.getElementById('pp-price').className = 'value';
        document.getElementById('send-pp').value = result.pp;
      }
      if (result.pvc) {
        document.getElementById('pvc-price').textContent = result.pvc;
        document.getElementById('pvc-price').className = 'value';
        document.getElementById('send-pvc').value = result.pvc;
      }
      const count = [result.pe, result.pp, result.pvc].filter(Boolean).length;
      document.getElementById('found-count').textContent = count > 0 ? `检测到 ${count} 个价格` : '未检测到价格，请手动输入';
    }
  } catch (e) {
    document.getElementById('found-count').textContent = '请在支持的行情页面使用';
  }
}

function sendToApp() {
  const pe = document.getElementById('send-pe').value;
  const pp = document.getElementById('send-pp').value;
  const pvc = document.getElementById('send-pvc').value;
  const params = new URLSearchParams();
  if (pe) params.set('pe', pe);
  if (pp) params.set('pp', pp);
  if (pvc) params.set('pvc', pvc);
  chrome.tabs.create({ url: `${SUJIATONG_URL}?${params.toString()}` });
}

loadPrices();
