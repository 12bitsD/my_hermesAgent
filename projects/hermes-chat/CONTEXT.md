# hermes-chat 当前架构状态

> 给未来的 Agent / 接手的人 — 项目现在长啥样
> 更新: 2026-06-04 (Phase 79 之后)

---

## 项目一句话

hermes-chat 是 **Hermes Agent 的 macOS/iOS 客户端**, 用 React Native + Expo
跑, 跟本地 hermes-agent gateway (127.0.0.1:8642) 通过 OpenAI 兼容 API 通信.
不是通用 chatbot, 是 Hermes-native 的 "phone remote to desktop" 客户端.

---

## 技术栈

| 层 | 选型 | 备注 |
|---|---|---|
| Framework | Expo SDK 51+ | Web / iOS / Android 同一 codebase |
| Language | TypeScript strict | 0 隐式 any |
| State | Zustand + AsyncStorage | 轻量, 持久化好 |
| UI | react-native (no native UI lib) | 自绘 + kawaii emoji |
| Network | aiohttp (gateway) / fetch (client) | OpenAI-compatible |
| Test | 0-dep stdlib only | `tsx tests/smoke.test.ts` 跑 23 个测试 |
| CI | GitHub Actions | 1 workflow, 跑 tsc + tests |
| Lint | tsc --noEmit | 当 lint + type check |

---

## 关键仓库 / 路径

| 路径 | 角色 | 我的 |
|---|---|---|
| `~/Desktop/CodeSpace/hermes-chat` | 客户端 (TypeScript) | ✅ 12bitsD |
| `~/Desktop/hermes-agent` | 上游 gateway (Python aiohttp) | ❌ NousResearch, 不动 |
| `~/Desktop/hermes-brain` | 知识库 (本仓库) | ✅ 12bitsD |
| `~/.hermes/` | hermes-agent 配置 + state.db | 改配置不动 schema |
| `~/.hermes/config.yaml` | LLM provider / model / port | gateway 启动读 |
| `~/.hermes/.env` | API keys (OPENAI, XIAOMI, MINIMAX_CN, etc.) | 不在 git |

---

## 客户端架构

### Source 目录

```
src/
├── components/
│   ├── chat/
│   │   ├── ChatView.tsx              # 主 chat 界面
│   │   ├── EmptyState.tsx            # 0 messages 时的 welcome 屏
│   │   ├── MessageBubble.tsx         # 单条消息
│   │   ├── Composer.tsx              # 输入框
│   │   ├── QuickActionSheet.tsx      # 4 quick action sheet
│   │   └── PairCodeCard.tsx          # 桌面端 pair code 显示
│   ├── layout/
│   │   ├── SessionDrawer.tsx         # 抽屉 (sessions / agent / tools)
│   │   └── PromptStrip.tsx           # prompt 列表
│   ├── SettingsPanel.tsx             # ⚙ Settings 弹层
│   ├── ApprovalModal.tsx             # 工具风险审批弹层
│   ├── ApprovalToast.tsx             # 工具审批 toast
│   └── win95/                        # 自绘 UI 组件
├── screens/
│   └── MainScreen.tsx                # 顶层 layout
├── services/
│   ├── llm/
│   │   ├── capabilities.ts           # /v1/capabilities 包装
│   │   ├── discover.ts               # "Find my Hermes" (Phase 79)
│   │   ├── endpointProbe.ts          # /health probe
│   │   └── models.ts                 # /v1/models 包装
│   ├── tools/                        # 工具调度
│   └── queue/
│       └── messageQueue.ts           # 消息队列 (含 retry + backoff)
├── domain/
│   ├── tools/risk.ts                 # 工具风险分级
│   └── settings/
│       ├── personas.ts               # 4 persona 预设 (Kawaii / Concise / Teacher / Catgirl)
│       └── ...
├── store/
│   ├── app.ts                        # 主 store (Zustand)
│   ├── useHermesSnapshot.ts          # 30s poll 4 endpoints + adaptive backoff (Phase 76)
│   └── useApprovalSession.ts
├── hooks/
│   ├── useNetworkStatus.ts           # 设备网络状态 (Phase 75)
│   ├── useDrawerSwipe.ts
│   └── ...
├── lib/
│   ├── pairCode.ts                   # 6 字符 code 生成 (Phase 78)
│   ├── hermesCliBus.ts               # window.hermes.* 事件总线
│   ├── chatSendBus.ts
│   └── ...
├── config/
│   └── app-constants.ts
└── utils/
    ├── platform.ts                   # isNarrow / isNative
    ├── theme.ts
    ├── haptic.ts
    └── ...
```

### 5 维产品打磨进度 (Phase 60-79)

| 维度 | 状态 | Phase 例子 |
|---|---|---|
| agent-native | ✅ | 60 (in-page CLI), 67 (run approval), 73 (CLI docs) |
| kawaii 浓度 | ✅ | 61 (sakura), 67 (mascot), 69 (state-aware mascot), 74 (4 personas) |
| trust | ✅ | 53 (5 态 status), 62 (offline queue), 64 (tool risk), 75 (offline hint) |
| 加/减法 | ✅ | 68 (删 Continue chip), 71 (CI), 76 (adaptive poll) |
| testing rigor | ✅ | 71 (13 tests), 72 (stop toggle test), 77 (snake-case) |
| **onboarding** | 🆕 | 78 (pair code, toy), 79 (Find my Hermes) |

---

## Phase 78 之后: 删 pair code UI, 改 mDNS discover

**Phase 78 错误**: 客户端生成 6 字符 code 显示在 Mac 屏幕上. 上游 hermes-agent
**没有** `/api/pair/redeem` 路由, 整个 flow 验证不了.

**Phase 79 修正**: 加 "Find my Hermes" 按钮在 Settings → Connection. 扫一组
known URL (127.0.0.1, localhost, hermes.local mDNS, 192.168.x.x 路由器) 让用户
点选. **0 上游改动**.

**下一步**: Phase 80+ 都是 hermes-chat 适配上游, 不会再动 hermes-agent.

---

## 5 维之外 — 当前真正的 backlog

按你 (user) 6/4 提的方向 + 我 audit 上游的发现:

| Phase | 内容 | 价值 | 改动范围 |
|---|---|---|---|
| 80 | Client-side retry + breaker (10s timeout, banner) | P0 stability | hermes-chat |
| 81 | 删 Phase 78 toy pair code, 改 "Settings → API Server" 提示 | P0 减法 | hermes-chat |
| 82 | Drawer 加 Connection health panel (/health/detailed) | P0 trust | hermes-chat |
| 83 | 动态拉 /v1/capabilities /skills 替代硬编码 | P1 agent-friendly | hermes-chat |
| 84 | EmptyState "How to use on phone" 引导卡 (Tailscale/Cloudflare) | P1 onboarding | hermes-chat |

---

## 测试 & CI

- **23/23 smoke tests pass** (Phase 79 后)
- **tsc --noEmit 干净** (0 错)
- **GitHub Actions workflow** 在 `.github/workflows/test.yml`, 跑 `npm test`
- **测试哲学**: 0 dep, 只用 stdlib (assert/test), 用真实环境 (不 mock)

---

## 当前 commit history (last 8)

```
f0240c4 Phase 79: Find my Hermes — gateway discovery from the client
418e30b Phase 78: QR-style 6-char pair code on desktop empty state
14a7fa6 feat: 90s anime style illustrations                    (sibling)
9a8b569 Phase 76: adaptive backoff on Hermes snapshot poll
a334be4 Phase 75: 📴 Offline composer hint
6e92928 Phase 74: 4 persona chips in Settings
de42c95 test: cover PERSONA_PRESETS in smoke suite           (sibling)
6720e1a Phase 73: teach Hermes about the in-page CLI in system prompt
```

---

## 上游 hermes-agent 现状 (audit 6/4)

- **61 个 .py 文件** in `gateway/platforms/`
- **31 个 platform adapter** (whatsapp / feishu / telegram / wecom / matrix / signal / yuanbao_proto / yuanbao_sticker / feishu_comment / dingtalk / api_server / etc.)
- **API server** (`api_server.py` 4228 行) 暴露: `/health`, `/health/detailed`, `/v1/{models,capabilities,skills,toolsets,chat/completions,responses}`, `/api/{sessions,jobs}`
- **DM pairing** (`pairing.py` 450 行) 8 字符 + SHA-256 + lockout + 0600 file
- **SessionDB** (`hermes_state.py` 1000+ 行) sqlite WAL + FTS5
- **没 device pair 路由** (我之前假设错了)
- **没 circuit breaker** (我之前加的 4 处 wrap 改的 — 现在 revert 了)

---

## 用户偏好 (从 memory / user profile 提取)

- 名字: 牢大, 我: 林小弟
- 中文为主, 风格: 二刺螈 / JOJO, 玩梗不加解释
- 工作风格: 强, 不降级, 测试暴露问题
- 撞墙才停, 不叫停就不停, phase 完成即 commit+push
- 物理层讲解风格 (讲解类内容必须加载 physical-layer-explanation skill)
- agent-friendly 哲学: 0 字段 / 0 endpoint / 0 key (auto-detect + override)

---

## 跨项目经验 (写给未来的 Agent)

1. **改 upstream 之前先 git remote -v** (撞墙: commit 9465b1bab 没权限 push)
2. **bash script 不要 inline secret** (撞墙: Bearer *** + write_file 替换)
3. **Node test 模块不能 import react-native** (撞墙: discover.ts 拉了 RN runtime)
4. **5 维饱和 ≠ 没活干** (撞墙: 漏了 onboarding)
5. **撞"撞墙"墙时退一步问"还有谁没考虑过"** (新用户 / 老用户回来 / 客户支持)
6. **改 upstream 之前先 audit** (撞墙: 假设没 pair 协议, 实际有 450 行 DM pairing)
7. **实现 flow 前先 verify server 端支持** (撞墙: Phase 78 6 字符 code 不能 verify)
