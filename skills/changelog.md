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

### 创建: svg-icon-generator (v2.0)
- **原因**: Agent 需要生成高质量 SVG icon
- **内容**: 支持 Anthropic 风格（渐变填充、温暖中性色）和 Lucide 风格
- **特点**: 色板系统、自检清单、路径生成技巧

## 2026-06-04

### 重大更新: hermes-chat 知识沉淀 (Phase 78-79 期间)

#### PITFALLS.md: 新增 10 条 (11-20)
- **11. Scope 越界**: 改 upstream, 浪费 30 min (撞墙案例 9465b1bab)
- **12. Bash heredoc glob 展开**: `***` 变空值
- **13. Write 工具 secret 替换**: 32 hex → `***`
- **14. RN import in Node test**: esbuild 炸
- **15. 假设上游没实现**: 实际有 450 行 DM pairing
- **16. CORS allow-list 漏 header**: 浏览器静默 403
- **17. Metro HMR 缓存 stale**: 改完浏览器不刷新
- **18. Phase 78 toy pair code**: server 端不支持, flow 断
- **19. Client-side breaker 测不出**: gateway 吞 model 错误
- **20. 用户不知 endpoint**: agent-friendly 缺第 6 维

#### DECISIONS.md: 全新 (15 个决策)
- 5 维产品打磨框架
- 5 维饱和 ≠ 没活干
- hermes-agent 不动, hermes-chat 适配 (Phase 79 revert 决策)
- client-side discover > server-side pair
- Node test 不能 import react-native
- 真实环境验证, 不 mock
- PHASES.md entry 模式
- pair code 客户端生成是 toy
- API key 不该让用户知道
- review 4 轮
- 自主 review
- commit + push 默认
- bash script 不要 inline secret
- 5 维饱和 + sibling 改 = 找别的 phase
- git history 不该改

#### CONTEXT.md: 全新 (架构 + 关键决策 + backlog)
- 项目一句话
- 技术栈
- 关键仓库 / 路径
- 客户端架构 (源目录树)
- 5 维产品打磨进度
- Phase 78 → 79 修正
- 5 维之外 backlog (Phase 80-84)
- 上游 hermes-agent 现状
- 用户偏好
- 跨项目经验 (7 条)

#### domain/hermes-best-practices.md: 新增 6 节
- 跨仓库操作 (upstream vs my-fork)
- 写脚本 / heredoc 注意事项
- Node test 兼容性
- 发现上游已实现什么
- 撞墙后处理 (饱和墙 / 撞墙撞墙)
- Hermes API 知识 (哪些路由存在, 哪些不存在)

#### domain/agent-behavior-patterns.md: 新增 8 个模式 (7-14)
- 撞"饱和"墙 — 实际漏了新维度
- Scope 越界 — 改 upstream
- 撞 hard wall 还能继续 — 换文件
- 假设上游没实现 — 实际有
- secret + bash heredoc + write_file 三重坑
- Node test 不能拉 RN runtime
- Client-side 测 breaker 测不出来
- 实现 flow 前先 verify server 端支持

### 关键认知升级

**核心 rule**: **改 hermes-chat 适配 hermes-agent, 不反过来**

**核心 rule**: **永远先 git remote -v, 确认是不是你的仓库**

**核心 rule**: **写 .sh 用 env var, 写完 cat 验证**

**核心 rule**: **util 模块不能 import react-native, 用 universal guard**

**核心 rule**: **实现 flow 前, 先 curl 验证 server 端支持**
