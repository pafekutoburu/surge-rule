# Surge 规则集 - 按服务商分类

基于 blackmatrix7/ios_rule_script + 自定义规则，完全展开去重。

## 统计

- 总规则数: 175866
- .list 文件数: 615
- 数据处理: 682 个外部规则集 → 展开后去重

## 使用方式

1. 将本仓库添加到 Surge
2. 在 [Rule] 中引用: `RULE-SET,https://raw.githubusercontent.com/<你的用户名>/<仓库名>/main/surge.conf,DIRECT`

## 规则集分类

| 策略 | 文件数 | 规则数 |
|------|--------|--------|
| AI | 1 | 120 |
| REJECT-TINYGIF | 19 | 122969 |
| DIRECT | 254 | 34088 |
| Proxy | 341 | 18678 |

## 自动刷新

每日自动从 blackmatrix7 仓库拉取最新规则，合并去重后推送更新。

## 使用方法

1. 在 Surge 的配置中引用 \`surge.conf\`
2. 确保 \`rules/\` 目录与 surge.conf 在同一级

## 文件结构

\`\`\`
surge-rules/
├── surge.conf             主配置文件 (直接给 Surge 用)
├── rules/                 615 个按服务商分类的 .list 文件
│   ├── AdGuardSDNSFilter.list
│   ├── Google.list
│   ├── Apple.list
│   ├── Netflix.list
│   └── ...
├── .github/workflows/     GitHub Actions 自动刷新
└── scripts/generate.py    规则生成脚本
\`\`\`

## 自动刷新

两种方案:

### A) GitHub Actions (推荐)
开启 Actions 后每天 UTC 2:00 自动刷新规则。

### B) 本地 Cron Job
\`\`\`bash
hermes cron create --schedule "0 10 * * *" \
  --prompt "下载最新 blackmatrix7 规则, 合并去重, 更新 ~/Desktop/surge-rules"
\`\`\`
