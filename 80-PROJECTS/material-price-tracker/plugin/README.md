# 塑价通浏览器插件

自动识别网页上的塑料期货价格（PE/PP/PVC），一键发送到塑价通。

## 文件结构

```
plugin/
├── manifest.json      # 扩展配置
├── popup.html        # 弹窗界面
├── popup.js         # 弹窗逻辑
├── content/
│   └── content.js   # 内容脚本：识别页面价格
├── background/
│   └── background.js # 后台脚本
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

## 安装步骤

1. 打开 Chrome，地址栏输入 `chrome://extensions/`
2. 右上角开启「开发者模式」
3. 点击「加载已解压的扩展程序」
4. 选择 `plugin/` 文件夹

## 图标

需要添加图标到 `icons/` 目录：
- icon16.png (16×16)
- icon48.png (48×48)
- icon128.png (128×128)

可用在线工具生成：https://favicon.io/

## 支持的页面

- 东方财富期货行情页
- 大连商品交易所官网
- 其他含有塑料期货价格表格的页面

## 使用方法

1. 打开支持行情页面
2. 点击地址栏右侧的塑价通图标
3. 检测到的价格自动显示
4. 点击「打开塑价通并填入」跳转

## 工作原理

content.js 会在页面中：
1. 查找含 PE/PP/PVC 关键词的表格单元格
2. 提取相邻的价格数字
3. 通过 Chrome Message API 与 popup 通信
