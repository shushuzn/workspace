# tests

Dashboard子系统的测试套件

## 测试文件

```
tests/
├── dashboard-api.test.js      # Dashboard API测试
├── dashboard-server.test.js   # Dashboard服务器测试
└── generate-dashboard-data.test.js  # 数据生成器测试
```

## 运行测试

```bash
npm test          # 单元测试（jest）
npm run test:e2e  # E2E测试（playwright）
```
