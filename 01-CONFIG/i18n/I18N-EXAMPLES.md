# i18n Dashboard - Usage Examples
# 双语仪表盘 - 使用示例

**快速测试指南 | Quick Test Guide**

---

## 1️⃣ 启动仪表盘 | Start Dashboard

```bash
# Windows
start-dashboard.bat

# Or manually
py dashboard-api-v4-persona.py
```

---

## 2️⃣ 测试 API | Test API

### 方法 1: 浏览器测试 | Browser Test

打开浏览器访问：

**中文版本:**
- http://localhost:8448/api/personas
- http://localhost:8448/api/dashboard?lang=zh
- http://localhost:8448/api/health/system

**English Version:**
- http://localhost:8448/api/personas?lang=en
- http://localhost:8448/api/dashboard?lang=en
- http://localhost:8448/api/health/system?lang=en

**语言列表 | Language List:**
- http://localhost:8448/api/i18n/languages

**所有翻译 | All Translations:**
- http://localhost:8448/api/i18n/translations?lang=en

---

### 方法 2: cURL 测试

```bash
# 获取所有人格状态 (中文)
curl http://localhost:8448/api/personas

# Get all personas (English)
curl http://localhost:8448/api/personas?lang=en

# 获取仪表板汇总 (双语)
curl http://localhost:8448/api/dashboard?lang=zh

# Get dashboard summary (English)
curl http://localhost:8448/api/dashboard?lang=en

# 获取系统健康 (带翻译标签)
curl http://localhost:8448/api/health/system?lang=en

# 获取支持的翻译
curl http://localhost:8448/api/i18n/translations?lang=en
```

---

### 方法 3: Python 测试脚本

```bash
py test-i18n-dashboard.py
```

---

## 3️⃣ 前端集成示例 | Frontend Integration

### JavaScript / Fetch API

```javascript
// 获取中文人格状态
async function getPersonasZh() {
  const response = await fetch('http://localhost:8448/api/personas?lang=zh');
  const data = await response.json();
  console.log('中文人格:', data);
  return data;
}

// Get personas in English
async function getPersonasEn() {
  const response = await fetch('http://localhost:8448/api/personas?lang=en');
  const data = await response.json();
  console.log('English Personas:', data);
  return data;
}

// 切换语言
async function switchLanguage(lang = 'zh') {
  const response = await fetch(`http://localhost:8448/api/dashboard?lang=${lang}`);
  const data = await response.json();
  
  // Update UI
  document.getElementById('dashboard-title').textContent = 
    lang === 'zh' ? data.title_zh : data.title_en;
  
  // Update labels
  for (const [key, value] of Object.entries(data.labels)) {
    const element = document.getElementById(`label-${key}`);
    if (element) {
      element.textContent = value;
    }
  }
}

// 使用示例
getPersonasZh();
getPersonasEn();
switchLanguage('en');
```

---

### React 组件示例

```jsx
import { useState, useEffect } from 'react';

function Dashboard({ language = 'zh' }) {
  const [personas, setPersonas] = useState({});
  const [stats, setStats] = useState(null);
  
  useEffect(() => {
    // Fetch personas with selected language
    fetch(`http://localhost:8448/api/personas?lang=${language}`)
      .then(res => res.json())
      .then(data => setPersonas(data));
    
    // Fetch statistics
    fetch(`http://localhost:8448/api/personas/statistics?lang=${language}`)
      .then(res => res.json())
      .then(data => setStats(data));
  }, [language]);
  
  return (
    <div className="dashboard">
      <h1>{language === 'zh' ? '创新者仪表盘' : 'Innovator Dashboard'}</h1>
      
      <div className="personas">
        {Object.entries(personas).map(([key, persona]) => (
          <div key={key} className="persona-card">
            <span className="icon">{persona.color}</span>
            <h3>{persona.role}</h3>
            <p>{persona.description}</p>
            <p>Status: {persona.status}</p>
          </div>
        ))}
      </div>
      
      {stats && (
        <div className="statistics">
          <h2>{stats.labels.tasks_completed}: {stats.total_tasks_completed}</h2>
          <h2>{stats.labels.success_rate}: {(stats.success_rate * 100).toFixed(1)}%</h2>
        </div>
      )}
      
      <button onClick={() => switchLanguage(language === 'zh' ? 'en' : 'zh')}>
        {language === 'zh' ? 'Switch to English' : '切换到中文'}
      </button>
    </div>
  );
}

export default Dashboard;
```

---

### Vue 3 组件示例

```vue
<template>
  <div class="dashboard">
    <h1>{{ lang.dashboardTitle }}</h1>
    
    <div class="language-switcher">
      <button @click="setLanguage('zh')" :class="{ active: currentLang === 'zh' }">
        中文
      </button>
      <button @click="setLanguage('en')" :class="{ active: currentLang === 'en' }">
        English
      </button>
    </div>
    
    <div class="personas">
      <div v-for="(persona, key) in personas" :key="key" class="persona-card">
        <span class="icon">{{ persona.color }}</span>
        <h3>{{ persona.role }}</h3>
        <p>{{ persona.description }}</p>
        <p>Status: {{ persona.status }}</p>
      </div>
    </div>
    
    <div class="statistics" v-if="stats">
      <h2>{{ stats.labels.tasks_completed }}: {{ stats.total_tasks_completed }}</h2>
      <h2>{{ stats.labels.success_rate }}: {{ (stats.success_rate * 100).toFixed(1) }}%</h2>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

const currentLang = ref('zh');
const personas = ref({});
const stats = ref(null);

const lang = computed(() => ({
  dashboardTitle: currentLang.value === 'zh' 
    ? '创新者仪表盘 v4.1 - 7 人格增强版'
    : 'Innovator Dashboard v4.1 - 7-Persona Enhanced'
}));

async function setLanguage(lang) {
  currentLang.value = lang;
  await fetchPersonas();
  await fetchStats();
}

async function fetchPersonas() {
  const res = await fetch(`http://localhost:8448/api/personas?lang=${currentLang.value}`);
  personas.value = await res.json();
}

async function fetchStats() {
  const res = await fetch(`http://localhost:8448/api/personas/statistics?lang=${currentLang.value}`);
  stats.value = await res.json();
}

onMounted(() => {
  fetchPersonas();
  fetchStats();
});
</script>
```

---

## 4️⃣ 响应示例 | Response Examples

### GET /api/dashboard?lang=zh

```json
{
  "title_zh": "创新者仪表盘 v4.1 - 7 人格增强版",
  "title_en": "Innovator Dashboard v4.1 - 7-Persona Enhanced",
  "timestamp": "2026-03-17T10:30:00",
  "personas": {
    "planner": {
      "persona": "planner",
      "status": "idle",
      "role": "规划者",
      "description": "任务分解与规划",
      "color": "🔵",
      "language": "zh"
    }
  },
  "statistics": {
    "total_tasks_completed": 42,
    "success_rate": 0.95
  },
  "labels": {
    "tasks_completed": "已完成任务",
    "success_rate": "成功率",
    "active_personas": "活跃人格"
  },
  "language": "zh",
  "supported_languages": ["zh", "en"]
}
```

### GET /api/dashboard?lang=en

```json
{
  "title_zh": "创新者仪表盘 v4.1 - 7 人格增强版",
  "title_en": "Innovator Dashboard v4.1 - 7-Persona Enhanced",
  "timestamp": "2026-03-17T10:30:00",
  "personas": {
    "planner": {
      "persona": "planner",
      "status": "idle",
      "role": "Planner",
      "description": "Task decomposition & planning",
      "color": "🔵",
      "language": "en"
    }
  },
  "statistics": {
    "total_tasks_completed": 42,
    "success_rate": 0.95
  },
  "labels": {
    "tasks_completed": "Tasks Completed",
    "success_rate": "Success Rate",
    "active_personas": "Active Personas"
  },
  "language": "en",
  "supported_languages": ["zh", "en"]
}
```

---

## 5️⃣ 常见用例 | Common Use Cases

### 用例 1: 多语言网站 | Multilingual Website

```javascript
// 根据用户浏览器语言自动切换
const userLang = navigator.language.startsWith('zh') ? 'zh' : 'en';

fetch(`http://localhost:8448/api/dashboard?lang=${userLang}`)
  .then(res => res.json())
  .then(data => renderDashboard(data));
```

### 用例 2: 用户手动切换 | Manual Language Toggle

```javascript
let currentLang = 'zh';

function toggleLanguage() {
  currentLang = currentLang === 'zh' ? 'en' : 'zh';
  localStorage.setItem('dashboard_lang', currentLang);
  loadDashboard();
}

function loadDashboard() {
  fetch(`http://localhost:8448/api/dashboard?lang=${currentLang}`)
    .then(res => res.json())
    .then(data => updateUI(data));
}
```

### 用例 3: 同时获取双语 | Fetch Both Languages

```javascript
async function getBilingualData() {
  const [zhData, enData] = await Promise.all([
    fetch('http://localhost:8448/api/personas?lang=zh').then(r => r.json()),
    fetch('http://localhost:8448/api/personas?lang=en').then(r => r.json())
  ]);
  
  return { zh: zhData, en: enData };
}
```

---

## 6️⃣ 故障排除 | Troubleshooting

### 问题：API 不响应 | API Not Responding

**解决 | Solution:**
```bash
# 检查服务器是否运行
curl http://localhost:8448/health

# 重启服务器
taskkill /F /IM python.exe
start-dashboard.bat
```

### 问题：中文显示乱码 | Chinese Characters Garbled

**解决 | Solution:**
```bash
# 确保终端使用 UTF-8
chcp 65001
py dashboard-api-v4-persona.py
```

### 问题：语言参数无效 | Invalid Language Parameter

**检查支持的语言:**
```bash
curl http://localhost:8448/api/i18n/languages
```

---

## 7️⃣ 性能优化建议 | Performance Tips

1. **缓存翻译** - 前端缓存翻译结果，减少 API 调用
2. **批量获取** - 使用 `/api/dashboard` 一次性获取所有数据
3. **WebSocket** - 使用 WebSocket 实时推送 (未来功能)

---

**🐾 Happy Coding! | 编程愉快!**
