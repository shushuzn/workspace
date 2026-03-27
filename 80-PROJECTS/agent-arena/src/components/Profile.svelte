<script>
  import { gameStore } from '../stores/gameStore.js';
  
  $: state = $gameStore;
  $: stats = state.stats || {};
  $: winRate = stats.totalBattles > 0 ? Math.round((stats.totalWins / stats.totalBattles) * 100) : 0;
  $: totalPower = state.agents.reduce((sum, a) => sum + a.power, 0);
  $: averagePower = state.agents.length > 0 ? Math.round(totalPower / state.agents.length) : 0;
  
  function formatDate(timestamp) {
    if (!timestamp) return '-';
    return new Date(timestamp).toLocaleDateString('zh-CN');
  }
  
  function resetGame() {
    if (confirm('确定要重置游戏吗?所有数据将被清空!')) {
      localStorage.removeItem('agent-arena-save');
      location.reload();
    }
  }
  
  function exportSave() {
    const data = JSON.stringify(state);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `agent-arena-save-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }
  
  function importSave(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result);
        gameStore.setState(data);
        localStorage.setItem('agent-arena-save', JSON.stringify(data));
        if (typeof gameStore.notify === 'function') {
          gameStore.notify({ message: '存档导入成功!', type: 'success' });
        }
      } catch (err) {
        if (typeof gameStore.notify === 'function') {
          gameStore.notify({ message: '存档导入失败!', type: 'error' });
        }
      }
    };
    reader.readAsText(file);
  }
</script>

<div class="profile-container">
  <div class="profile-header">
    <h2>👤 个人中心</h2>
    <p>查看你的游戏数据</p>
  </div>
  
  <!-- Stats Overview -->
  <div class="stats-grid">
    <div class="stat-card coins">
      <span class="stat-icon">🪙</span>
      <span class="stat-value">{state.coins.toLocaleString()}</span>
      <span class="stat-label">金币</span>
    </div>
    <div class="stat-card gems">
      <span class="stat-icon">💎</span>
      <span class="stat-value">{state.gems.toLocaleString()}</span>
      <span class="stat-label">钻石</span>
    </div>
    <div class="stat-card agents">
      <span class="stat-icon">🤖</span>
      <span class="stat-value">{state.agents.length}</span>
      <span class="stat-label">Agent</span>
    </div>
    <div class="stat-card battles">
      <span class="stat-icon">⚔️</span>
      <span class="stat-value">{stats.totalBattles || 0}</span>
      <span class="stat-label">战斗</span>
    </div>
  </div>
  
  <!-- Performance -->
  <div class="performance-section">
    <h3>📊 战绩统计</h3>
    <div class="performance-grid">
      <div class="perf-item">
        <span class="perf-label">胜率</span>
        <span class="perf-value win">{winRate}%</span>
      </div>
      <div class="perf-item">
        <span class="perf-label">胜场</span>
        <span class="perf-value success">{stats.totalWins || 0}</span>
      </div>
      <div class="perf-item">
        <span class="perf-label">负场</span>
        <span class="perf-value danger">{(stats.totalBattles || 0) - (stats.totalWins || 0)}</span>
      </div>
      <div class="perf-item">
        <span class="perf-label">总战力</span>
        <span class="perf-value">{totalPower.toLocaleString()}</span>
      </div>
      <div class="perf-item">
        <span class="perf-label">平均战力</span>
        <span class="perf-value">{averagePower}</span>
      </div>
      <div class="perf-item">
        <span class="perf-label">抽卡次数</span>
        <span class="perf-value">{stats.totalPulls || 0}</span>
      </div>
    </div>
  </div>
  
  <!-- Collection Summary -->
  {#if state.agents.length > 0}
    <div class="collection-section">
      <h3>📁 收藏概览</h3>
      <div class="collection-rarity">
        {#each ['common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic'] as rarity}
          {@const count = state.agents.filter(a => a.rarity === rarity).length}
          {#if count > 0}
            <div class="rarity-stat {rarity}">
              <span class="rarity-name">{rarity}</span>
              <span class="rarity-count">x{count}</span>
            </div>
          {/if}
        {/each}
      </div>
    </div>
  {/if}
  
  <!-- Save Management -->
  <div class="save-section">
    <h3>💾 存档管理</h3>
    <div class="save-actions">
      <button class="save-btn" on:click={exportSave}>
        📤 导出存档
      </button>
      <label class="save-btn import-btn">
        📥 导入存档
        <input type="file" accept=".json" on:change={importSave} style="display: none" />
      </label>
    </div>
    <p class="save-hint">存档自动保存到浏览器本地存储</p>
  </div>
  
  <!-- Game Info -->
  <div class="info-section">
    <h3>ℹ️ 游戏信息</h3>
    <div class="info-grid">
      <div class="info-item">
        <span class="info-label">创建日期</span>
        <span class="info-value">{formatDate(stats.createdAt)}</span>
      </div>
      <div class="info-item">
        <span class="info-label">游戏版本</span>
        <span class="info-value">v1.0.0</span>
      </div>
    </div>
  </div>
  
  <!-- Danger Zone -->
  <div class="danger-section">
    <h3>⚠️ 危险区域</h3>
    <button class="reset-btn" on:click={resetGame}>
      🗑️ 重置游戏
    </button>
  </div>
</div>

<style>
  .profile-container { display: flex; flex-direction: column; gap: 1.5rem; }
  .profile-header { text-align: center; padding: 1rem; background: linear-gradient(135deg, rgba(168, 85, 247, 0.2) 0%, rgba(236, 72, 153, 0.2) 100%); border-radius: 1rem; border: 1px solid rgba(168, 85, 247, 0.3); }
  .profile-header h2 { font-size: 1.25rem; margin-bottom: 0.25rem; }
  .profile-header p { font-size: 0.85rem; color: #a0a0a0; }
  
  .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem; }
  .stat-card { display: flex; flex-direction: column; align-items: center; padding: 1rem; background: rgba(255, 255, 255, 0.05); border-radius: 1rem; border: 1px solid rgba(255, 255, 255, 0.1); }
  .stat-icon { font-size: 1.5rem; margin-bottom: 0.25rem; }
  .stat-value { font-size: 1.25rem; font-weight: 700; }
  .stat-label { font-size: 0.75rem; color: #a0a0a0; }
  .stat-card.coins .stat-value { color: #f59e0b; }
  .stat-card.gems .stat-value { color: #a855f7; }
  .stat-card.agents .stat-value { color: #667eea; }
  .stat-card.battles .stat-value { color: #ef4444; }
  
  .performance-section, .collection-section, .save-section, .info-section, .danger-section { padding: 1rem; background: rgba(255, 255, 255, 0.05); border-radius: 1rem; }
  h3 { font-size: 0.9rem; margin-bottom: 0.75rem; color: #a0a0a0; }
  
  .performance-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; }
  .perf-item { display: flex; flex-direction: column; align-items: center; padding: 0.75rem; background: rgba(255, 255, 255, 0.03); border-radius: 0.75rem; }
  .perf-label { font-size: 0.75rem; color: #a0a0a0; margin-bottom: 0.25rem; }
  .perf-value { font-size: 1.1rem; font-weight: 700; }
  .perf-value.win { color: #10b981; }
  .perf-value.success { color: #10b981; }
  .perf-value.danger { color: #ef4444; }
  
  .collection-rarity { display: flex; flex-wrap: wrap; gap: 0.5rem; }
  .rarity-stat { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0.75rem; border-radius: 0.5rem; font-size: 0.85rem; }
  .rarity-stat.common { background: rgba(156, 163, 175, 0.2); border: 1px solid #9ca3af; }
  .rarity-stat.uncommon { background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; }
  .rarity-stat.rare { background: rgba(59, 130, 246, 0.2); border: 1px solid #3b82f6; }
  .rarity-stat.epic { background: rgba(168, 85, 247, 0.2); border: 1px solid #a855f7; }
  .rarity-stat.legendary { background: rgba(245, 158, 11, 0.2); border: 1px solid #f59e0b; }
  .rarity-stat.mythic { background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; }
  .rarity-name { text-transform: capitalize; }
  .rarity-count { font-weight: 700; }
  
  .save-actions { display: flex; gap: 0.75rem; }
  .save-btn { flex: 1; padding: 0.75rem; background: rgba(102, 126, 234, 0.2); border: 1px solid rgba(102, 126, 234, 0.3); border-radius: 0.75rem; color: #fff; cursor: pointer; transition: all 0.2s; text-align: center; }
  .save-btn:hover { background: rgba(102, 126, 234, 0.3); }
  .save-hint { font-size: 0.75rem; color: #a0a0a0; margin-top: 0.5rem; text-align: center; }
  
  .info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; }
  .info-item { display: flex; justify-content: space-between; padding: 0.5rem; background: rgba(255, 255, 255, 0.03); border-radius: 0.5rem; font-size: 0.85rem; }
  .info-label { color: #a0a0a0; }
  .info-value { font-weight: 600; }
  
  .danger-section { border: 1px solid rgba(239, 68, 68, 0.3); }
  .reset-btn { width: 100%; padding: 0.75rem; background: rgba(239, 68, 68, 0.2); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 0.75rem; color: #ef4444; cursor: pointer; transition: all 0.2s; }
  .reset-btn:hover { background: rgba(239, 68, 68, 0.3); }
</style>
