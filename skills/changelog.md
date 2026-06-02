# Skill 变更日志

> 记录所有 skill 的创建和修改，便于追踪 Agent 行为改进

## 2026-06-03

### 创建: autonomous-product-shipping
- **原因**: 从历史 session 中发现 Agent 在长任务中反复停止、方向偏离
- **内容**: 自主产品交付的操作合同，包含 phase 报告节奏、意图对齐规则
- **关联问题**: Agent 自行停止、方向漂移

### 创建: iterative-product-polish
- **原因**: 用户多次要求"逼近极限"但 Agent 不知道何时停止
- **内容**: 5 维产品打磨 checklist，screenshot critique 流程
- **关联问题**: Agent 过早停止、质量不达标

### 创建: kawaii-concentration-boost
- **原因**: 用户要求提升"二次元浓度"但 Agent 不知道具体怎么做
- **内容**: 5 步提升浓度的具体操作流程
- **关联问题**: 方向偏离、不知道如何实现审美需求

### 修改: hermes-chat 相关 skills
- **变更**: 更新了 PITFALLS.md，加入从 session 分析中提取的踩坑记录
- **影响**: 下次开 hermes-chat 时自动加载，避免重复犯错
