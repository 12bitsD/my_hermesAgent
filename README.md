# 🧠 my_hermesAgent — Hermes Agent 自迭代知识库

> 通过历史 session 数据分析，持续发现 Agent 问题、提炼经验、改进行为。

## 这个仓库是什么

这是我（Hermes Agent）的"外挂大脑"。它不存储每 turn 的热数据（那是 memory 的活），
而是存储：

- **项目上下文** — 每个项目的状态、决策、踩坑记录
- **行为分析** — 从 8000+ 历史 session 中挖掘的 Agent 行为模式
- **改进方案** — 针对发现的问题的具体修复措施
- **领域知识** — 跨项目的技术经验积累

## 目录结构

```
hermes-brain/
├── README.md                          # 你正在读的这个
├── analyze_sessions.py                # Session 分析脚本（手动跑）
├── nightly_scan.py                    # 每日自动扫描脚本（cron 调用）
│
├── reports/                           # 分析报告（按日期）
│   ├── 2026-06-03/
│   │   ├── summary.md                 # 当日 session 摘要
│   │   └── findings.md                # 发现的问题和建议
│   └── archive/
│       └── 2026-06-03-initial.md      # 初始全量分析
│
├── projects/                          # 每个项目一个目录
│   └── hermes-chat/
│       ├── CONTEXT.md                 # 当前架构状态
│       ├── PITFALLS.md                # 踩过的坑（从历史 session 提取）
│       └── DECISIONS.md               # 关键决策日志
│
├── domain/                            # 领域知识
│   ├── agent-behavior-patterns.md     # Agent 行为模式总结
│   └── hermes-best-practices.md       # Hermes 使用最佳实践
│
└── skills/                            # Skill 变更记录
    └── changelog.md                   # Skill 创建/修改日志
```

## 如何使用

### 手动分析
```bash
cd ~/Desktop/hermes-brain
python3 analyze_sessions.py --all                    # 全局统计
python3 analyze_sessions.py --session SESSION_ID     # 单 session 分析
```

### 自动分析
每天 21:00 cron job 自动扫描当天的 session，生成报告到 `reports/` 目录。

### Agent 使用
每次新 session 开始时，Agent 会读取:
1. `projects/<当前项目>/PITFALLS.md` — 避免重复犯错
2. `domain/agent-behavior-patterns.md` — 应用已知的最佳实践

## 数据来源

- `~/.hermes/state.db` — SQLite 数据库，存储所有 session 和消息
- 分析脚本直接查询数据库，不依赖网络
- GitHub push 由 cron job 每天自动执行

## 关键指标

| 指标 | 当前值 |
|------|--------|
| 历史 session 总数 | 8,279 |
| 总 tool 调用 | 71,476 |
| 空响应率（MiniMax-M3）| 19.3% |
| 用户纠正最高频问题 | Agent 自行停止 |
| Tool 错误率 | 34% |

---
*由 Hermes Agent 自动维护*
