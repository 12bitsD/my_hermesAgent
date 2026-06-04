# hermes-chat 关键决策日志

> 记录项目里做的非显然决策 — 为什么这么做, 当时考虑了啥
> 写给未来的自己 / 接手的人
> 更新: 2026-06-04

---

## 决策 1: 5 维产品打磨框架 (Phase 60-77)

**背景**: 用户说"逼近极限", 但不知道"极限"是啥
**选项考虑**:
- A) 用户定 5 维, 我执行
- B) 我定 5 维, 每次过 review
- C) 不定, 自由发挥

**选 B**: 5 维 = agent-native / kawaii 浓度 / trust / 加减法 / testing rigor
**为什么**: 用户没空想 5 维是啥, 但知道"产品不行"长啥样
**副作用**: 撞软墙时容易觉得 "5 维都覆盖了, 没事可做" → 错过真正缺的东西 (onboarding)
**修正**: Phase 79 撞墙后, 加入第 6 维 "onboarding completeness" (新用户能否 0 指导上手)

---

## 决策 2: 5 维饱和 ≠ 没活干 (Phase 78 撞硬墙)

**背景**: Phase 78 后我宣布"5 维饱和, 撞硬墙"
**真相**: 我漏了 onboarding story. 5 维全做完了, 但 "5 维全是开发者视角", 真实用户首次开 app 啥都不懂
**Lesson**: 撞"饱和"墙时, 退一步问"还有谁没考虑过" — 新用户, 老用户离开再回来, 客户的支持团队, 等等

---

## 决策 3: hermes-agent 不动, hermes-chat 适配 (Phase 79 revert)

**背景**: 6/4 我 commit 了 `9465b1bab` 改 hermes-agent (加 circuit breaker + 4 处 _run_agent wrap)
**真相**: hermes-agent 是 NousResearch 上游仓库, 我 (12bitsD) 没 push 权限. 改动只在本地
**正确做法**: **改 hermes-chat 去适配 hermes-agent**, 不反过来
**revert 操作**: `git reset --hard b9646276f` 回到上游最后 commit
**Lesson**: 任何仓库先 `git remote -v` 确认是不是你的. 上游 (upstream) 改了也推不上去
**可借鉴**: hermes-agent 的 `gateway/pairing.py` 已有完整 DM pairing (8 字符 + SHA-256 + lockout), 我可以**借鉴它的安全模式**到 hermes-chat 的 device discovery, 但**不复制代码**

---

## 决策 4: client-side discover > server-side pair (Phase 79)

**选项**:
- A) 改 hermes-agent 加 `/api/pair/redeem` 路由 (我改不了)
- B) Phase 78 客户端 6 字符 code + 假设上游有 verify (上游没有, toy-grade)
- C) 客户端 mDNS + LAN IP discover ("Find my Hermes" 按钮) + 用户手填

**选 C**: 零修改上游, 用户体验跟"扫二维码"差不多
**为什么 C 是对的**: 真实场景里, hermes-chat 跟 hermes-agent **永远在同一台 Mac** (Mac 跑 agent, 浏览器在 Mac 上访问, 或 Tailscale 走 .local). 根本不需要 "device pair", **device 就是 Mac**. 用户需要的只是"我 Mac 的 IP 是啥" — mDNS / 路由器 IP 列表能解决 90%

**Lesson**: 实现"流程"前, 先 audit 上游是不是支持, 不支持的找客户端 workaround, 别动上游

---

## 决策 5: 客户端 Node test 不能 import react-native (Phase 79)

**背景**: discover.ts 想用 `isNarrow` from `utils/platform`, import 触发 react-native 整个 runtime
**后果**: `tsx tests/smoke.test.ts` esbuild 失败 "Unexpected 'typeof' at react-native/index.js:27"
**修复**: util 模块用 `typeof window !== 'undefined' && window.innerWidth` 内联检测
**Rule**: 任何会被 Node smoke test 引用的 module, 不能 import react-native. 只用 `typeof window/document/navigator` 这种 universal guard
**影响**: 全项目 util 都得审视, 不光是新加的. 0-dep test 哲学要求 util 模块能跑 Node

---

## 决策 6: 真实环境验证, 不 mock (continuous)

**背景**: 我之前写 hermes-chat 的 smoke test 一直用 mock (fetch 不发, store 是空)
**修正**: 真实环境验证, 但**用真实 hermes-agent gateway** (我 Mac 上的 8642)
**实现**: test 跑 `discoverGateway()` 真实发 fetch, 10s budget 内能跟 127.0.0.1:8642 通信就 OK
**好处**: 0 dep + 真实环境, 不假装
**坏处**: 跑 test 慢 (10s 因为 discover budget), CI 上要 accept
**判断**: 慢一点比假装快更值. 测出"找不到 gateway"跟测出"找到"是**不同信息**, 都能测

---

## 决策 7: 每个 phase 写 PHASES.md entry (Phase 70)

**背景**: 18 个 phase 没文档, 接手的人不知道为啥
**选项**:
- A) commit message 里写 (历史, 不聚合)
- B) PHASES.md 表格 (聚合, 一页看所有)
- C) inline comments (分散)

**选 B**: PHASES.md 66 行表格, 每次 commit 追加
**好处**: review 时一页看完所有 phase
**代价**: 每次 commit 得多改一个文件, 但不大
**Lesson**: 文档化是 developer experience, 不是 overhead. 晚做不如早做

---

## 决策 8: pair code 不存 server-side 时, 客户端生成 (Phase 78 → 79 修正)

**Phase 78 假设**: hermes-agent 没 pair 路由, 我用客户端 Math.random 生成 6 字符 code 显示给用户
**Phase 79 修正**: 这是 **toy-grade**, 整个 flow 是断的 (server 不能 verify). 删掉, 改 mDNS discover
**Lesson**: 实现一个 flow 之前, **先确认 server 端支持**. 不支持就明确告诉用户"这个 flow 是 demo"

---

## 决策 9: 不让 user 知道 API key 是什么 (产品哲学)

**背景**: 用户问 "API key 跟 SP 是干啥的"
**之前回答**: "鉴权 + 身份握手" — 对的但太开发者
**真实回答**: 用户**应该不感知**这些字段. hermes-chat 应该 auto-detect + 隐藏
**当前实现**: Settings 还能看到 key 字段, 但 "Find my Hermes" 按钮让用户不用手填 endpoint
**未来**: 把 API key 字段折叠到 "Advanced", 默认隐藏
**Lesson**: agent-friendly = 0 字段, 0 endpoint, 0 key. 用户只看到 "Hermes on" / "Hermes off"

---

## 决策 10: review style — 4 轮 (tech / requirements / product / design)

**用户要求** (2026-06-03): "每 phase 走 4 轮, 分阶段汇报别 batch"
**做什么**: 4 个 review lens, 每个 5-10 min, 中间会改 scope (收紧 / 改造 vs 删除)
**真价值**: 中间产生的 plan 变化, 不只是 GO/NO-GO 结论
**3 类 valuable catch**:
- (a) 救 catastrophic design (工具风险分级)
- (b) 划清责任边界 ("前向投资" 不揽 server bug)
- (c) 区分相似但不同的 failure mode (网络 offline vs server offline)
**Lesson**: review 是中间产物, 不是终点. 抓 scope 变化才是 review 的价值

---

## 决策 11: 自主模式延伸到 review (2026-06-03)

**用户偏好**: "做 N 个 review" = 自主跑完全部 + 一次汇报, 不等 ack
**之前**: 走完一个 phase 停下来 ping user
**现在**: 自主跑到 N 个 review 都做完, 一次汇报全部
**风险**: user 中途想法变了, 走过头
**缓解**: review 中 plan 变化要明显, user 能 catch

---

## 决策 12: commit + push 是默认 (2026-06-02)

**用户明确**: "可以直接提交push", "phase 完成即 commit+push+汇报"
**之前**: 写完代码, 问 user "要 commit 吗", user 答 "commit 吧", 浪费一个 turn
**现在**: 写完代码, **直接** `git add src/ && git commit -m "..." && git push`
**例外**: 涉及 destructive (rm / reset --hard / rebase / force push) 仍问
**Lesson**: 重复性确认 = overhead. 默认同意 + 显式撤回 > 每次都问

---

## 决策 13: bash script 不要 inline secret (Phase 79 撞墙)

**症状**: `Authorization: Bearer ***` 出现 `***` 变 glob, 后续 `=***` 啥的不是 flag
**修复**: `K="5ba3863bd0be0c9d2de2b3eb1def16c3"` 单独 var, curl 引用
**Lesson**: 写 test 脚本时, key 用 env var. write_file 看到 32 字符 hex 也会替换 `***`, 双重保险

---

## 决策 14: 5 维饱和 + sibling 在改 = 找别的 phase (Phase 76-79)

**撞墙**: SessionDrawer + MainScreen 被 sibling 改, 我不能用
**不撞 sibling 策略**:
- 改 ChatView (Phase 75)
- 改 useHermesSnapshot (Phase 76)
- 改 lib/pairCode (Phase 78)
- 改 lib/discover (Phase 79)
**结果**: 0 冲突, 4 个 phase 顺利落地
**Lesson**: 撞 hard wall 不一定是"没活干", 也可以是"换个文件". sibling 在改的我避开, 其他文件还能动

---

## 决策 15: git history 不该改 (Phase 79 revert)

**撞墙**: 6/4 commit `9465b1bab` 改 hermes-agent 错了
**做法**: `git reset --hard b9646276f` 撤回
**没做**: `git rebase -i HEAD~1` 改 message (改 history 影响其他协作)
**Lesson**: commit 错了 revert, 不要 amend. history 是事实, 不要回溯重写
