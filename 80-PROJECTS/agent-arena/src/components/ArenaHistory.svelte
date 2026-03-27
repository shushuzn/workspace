<script>
  import { arenaStore } from '../stores/arenaStore';

  let expandedId = null;

  function toggleExpand(id) {
    expandedId = expandedId === id ? null : id;
  }

  function formatDate(timestamp) {
    const d = new Date(timestamp);
    return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  }

  function goBack() {
    arenaStore.reset();
  }

  $: history = $arenaStore.history || [];
</script>

<div class="history-container">
  <div class="history-header">
    <h2>竞技场记录</h2>
    <button class="back-btn" on:click={goBack}>← 返回</button>
  </div>

  {#if history.length === 0}
    <div class="empty-state">
      <p>暂无对战记录</p>
      <button class="btn-primary" on:click={() => arenaStore.setStage('STAGE_SELECT')}>
        开始挑战
      </button>
    </div>
  {:else}
    <div class="history-list">
      {#each history as record (record.id)}
        <div class="history-item" role="button" tabindex="0" on:click={() => toggleExpand(record.id)} on:keydown={(e) => e.key === 'Enter' && toggleExpand(record.id)}>
          <div class="item-main">
            <div class="item-left">
              <span class="opponent-avatar">{record.avatar}</span>
              <div class="opponent-info">
                <span class="opponent-name">{record.name}</span>
                <span class="personality-tag">{record.personality}</span>
              </div>
            </div>
            <div class="item-right">
              <span class="result-badge {record.result}">
                {record.result === 'win' ? '胜利' : '失败'}
              </span>
              <span class="rewards">
                +{record.rewards?.xp || 0}XP +{record.rewards?.coins || 0}币
              </span>
            </div>
          </div>
          <div class="item-meta">
            <span class="timestamp">{formatDate(record.createdAt)}</span>
            <span class="expand-hint">{expandedId === record.id ? '▲' : '▼'}</span>
          </div>
          {#if expandedId === record.id}
            <div class="backstory-expanded">
              {record.backstory}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .history-container { display: flex; flex-direction: column; padding: 1rem; }
  .history-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
  .history-header h2 { margin: 0; }
  .back-btn { background: none; border: none; color: #4caf50; cursor: pointer; font-size: 1rem; }
  .empty-state { text-align: center; padding: 3rem; color: #888; }
  .empty-state p { margin-bottom: 1rem; }
  .history-list { display: flex; flex-direction: column; gap: 0.5rem; }
  .history-item { background: #1a1a1a; border-radius: 8px; padding: 0.75rem; cursor: pointer; }
  .item-main { display: flex; justify-content: space-between; align-items: center; }
  .item-left { display: flex; align-items: center; gap: 0.75rem; }
  .opponent-avatar { font-size: 1.5rem; }
  .opponent-info { display: flex; flex-direction: column; }
  .opponent-name { font-weight: bold; }
  .personality-tag { font-size: 0.75rem; color: #888; }
  .item-right { display: flex; flex-direction: column; align-items: flex-end; gap: 0.25rem; }
  .result-badge { padding: 0.125rem 0.5rem; border-radius: 1rem; font-size: 0.75rem; font-weight: bold; }
  .result-badge.win { background: #4caf50; color: white; }
  .result-badge.lose { background: #f44336; color: white; }
  .rewards { font-size: 0.75rem; color: #888; }
  .item-meta { display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.75rem; color: #666; }
  .expand-hint { color: #666; }
  .backstory-expanded { margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid #333; font-size: 0.875rem; color: #aaa; font-style: italic; }
  .btn-primary { background: #4caf50; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; cursor: pointer; }
</style>
