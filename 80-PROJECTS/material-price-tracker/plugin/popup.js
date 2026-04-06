const SUJIATONG_URL = 'https://material-price-tracker.vercel.app';
const ALERT_CONFIG_KEY = 'priceAlertConfig';

// 加载告警配置
function loadAlertConfig() {
  const stored = localStorage.getItem(ALERT_CONFIG_KEY);
  if (stored) {
    try {
      const config = JSON.parse(stored);
      document.getElementById('alert-pe').value = config.peThreshold || '';
      document.getElementById('alert-pp').value = config.ppThreshold || '';
      document.getElementById('alert-pvc').value = config.pvcThreshold || '';
      document.getElementById('webhook-url').value = config.webhookUrl || 'http://localhost:8000/webhook';
    } catch (e) {}
  }
}

// 保存告警配置
function saveAlertConfig() {
  const config = {
    peThreshold: document.getElementById('alert-pe').value,
    ppThreshold: document.getElementById('alert-pp').value,
    pvcThreshold: document.getElementById('alert-pvc').value,
    webhookUrl: document.getElementById('webhook-url').value,
  };
  localStorage.setItem(ALERT_CONFIG_KEY, JSON.stringify(config));
  const status = document.getElementById('alert-status');
  status.textContent = '✓ 配置已保存';
  setTimeout(() => { status.textContent = ''; }, 2000);
}

// 检测价格是否触发阈值并发送 webhook
async function checkAndTriggerAlert(prices) {
  const stored = localStorage.getItem(ALERT_CONFIG_KEY);
  if (!stored) return;
  try {
    const config = JSON.parse(stored);
    const alerts = [];
    if (prices.pe && config.peThreshold && parseFloat(prices.pe) <= parseFloat(config.peThreshold)) {
      alerts.push({ type: 'PE', price: prices.pe, threshold: config.peThreshold });
    }
    if (prices.pp && config.ppThreshold && parseFloat(prices.pp) <= parseFloat(config.ppThreshold)) {
      alerts.push({ type: 'PP', price: prices.pp, threshold: config.ppThreshold });
    }
    if (prices.pvc && config.pvcThreshold && parseFloat(prices.pvc) <= parseFloat(config.pvcThreshold)) {
      alerts.push({ type: 'PVC', price: prices.pvc, threshold: config.pvcThreshold });
    }
    if (alerts.length === 0 || !config.webhookUrl) return;
    const payload = {
      source: 'material-price-tracker',
      timestamp: new Date().toISOString(),
      alerts: alerts.map(a => ({
        type: a.type,
        currentPrice: parseFloat(a.price),
        threshold: parseFloat(a.threshold),
        triggered: true,
      })),
    };
    try {
      const resp = await fetch(config.webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const status = document.getElementById('alert-status');
      if (resp.ok) {
        status.textContent = '🚨 告警已触发并推送';
      } else {
        status.textContent = '告警触发但推送失败';
        status.style.color = '#e74c3c';
      }
      setTimeout(() => { status.textContent = ''; status.style.color = '#27ae60'; }, 3000);
    } catch (e) {
      const status = document.getElementById('alert-status');
      status.textContent = 'Webhook 请求失败';
      status.style.color = '#e74c3c';
      setTimeout(() => { status.textContent = ''; status.style.color = '#27ae60'; }, 3000);
    }
  } catch (e) {}
}

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
      // 检查是否触发告警
      checkAndTriggerAlert(result);
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
loadAlertConfig();
