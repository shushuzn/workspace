// 后台脚本：管理扩展状态
chrome.runtime.onInstalled.addListener(() => {
  console.log('[塑价通插件] 已安装 v1.0.0');
});

// 图标点击时刷新当前页面的价格检测
chrome.action.onClicked.addListener(async (tab) => {
  // 实际点击会打开 popup，这里可以留空
});
