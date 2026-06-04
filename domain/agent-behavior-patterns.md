# Agent 行为模式分析

> 基于 8279 个 session、254.4M tokens 的数据分析
> 最后更新: 2026-06-04 (Phase 79 撞墙后追加)

## 模式 1: 自主停止综合症

**数据**: 在 hermes-chat 长 session 中出现 5+ 次
**用户反应**: "怎么停了"、"为什么停了"、"？继续持续去迭代啊不要停下来"

**触发条件**:
- max_turns 到达上限
- context compaction 后 agent 失去上下文
- 完成一个子任务后没有自动衔接下一个

**修复方案**:
1. 自主模式下，剩余 10 个 turn 时主动报告
2. 子任务完成后自动检查是否还有待办
3. memory 中记录"不叫停就不停"的偏好

## 模式 2: 方向漂移

**数据**: 在多个长 session 中被用户纠正
**用户反应**: "我提醒下，你好像跑偏了"

**触发条件**:
- 长时间无用户输入（>30 min）
- context compaction 后丢失原始意图
- 过度关注技术细节而忘记产品目标

**修复方案**:
1. 每 5-10 个 turn 做一次意图对齐检查
2. 自问："我还在做用户要的东西吗？"
3. 读取项目的 CONTEXT.md 确认方向

## 模式 3: 批量修改风险

**数据**: 最大 session 中 patch→patch→patch 模式出现 66 次
**工具错误率**: 34%

**触发条件**:
- 一次修改多个文件
- 修改后不立即验证
- 前一个 patch 出错但继续执行后续 patch

**修复方案**:
1. 每 3-5 个 patch 做一次 tsc --noEmit 验证
2. patch 前先 read_file 确认目标内容
3. tool 返回 error 时立即处理

## 模式 4: Git 操作遗忘

**数据**: 用户多次提醒"记得 git push"
**影响**: 代码丢失风险、用户信任下降

**修复方案**:
1. 每完成一个功能点就 commit+push
2. memory 中记录"git push 是默认操作"
3. 自主模式下不需要用户确认

## 模式 5: Tool 错误不感知

**数据**: 34% 的 tool call 有错误输出
**常见错误**: patch 找不到目标、terminal 语法错误

**修复方案**:
1. tool 返回 error 时立即分析原因
2. 不要"假装没看到错误继续执行"
3. LSP cache 假报错: tsc --noEmit 干净就是真 OK

## 模式 6: 模型表现差异

| 模型 | 空响应率 | 特点 |
|------|---------|------|
| MiniMax-M3 | 19.3% | 最稳定，适合长 session |
| deepseek-v4-pro | 61.7% | 中等 |
| mimo-v2.5 | 84.7% | 空响应多，适合短任务 |
| kimi-for-coding | 92.6% | 主要用于 cron |

**建议**: 长时间自主迭代用 MiniMax-M3，短任务用 mimo-v2.5

## 模式 7: 撞"饱和"墙 — 实际漏了新维度 (6/4 新增)

**数据**: Phase 78 期间我宣布"5 维饱和, 没活干", 用户提醒"继续"
**真相**: 5 维都是开发者视角, 真实用户首次开 app 啥都不懂
**症状**:
- 撞"5 维都覆盖了"墙
- backlog 里 0 客户端可 push 的项
- sibling 在改的不能动
**修复方案**:
1. 退一步问"还有谁没考虑过" — 新用户 / 老用户回来 / 客户支持
2. 加第 6 维 "onboarding completeness" (新用户能否 0 指导上手)
3. audit 上游 (hermes-agent 已有啥, 我能借鉴/适配啥)

## 模式 8: Scope 越界 — 改 upstream (6/4 新增)

**数据**: 6/4 commit `9465b1bab` 改 hermes-agent (NousResearch 上游) 加 circuit breaker
**症状**:
- commit 后才发现 origin 是 upstream, 没 push 权限
- 改的东西推不上去, 浪费 30 min
- 改的是 contract, 不是 client
**修复方案**:
1. 改仓库之前永远先 `git remote -v`
2. 区分 upstream contract (不动) vs my-fork (自由改)
3. 改 hermes-chat 适配 hermes-agent, 不反过来
4. 改完发现没权限, `git reset --hard <last-good>` 撤回

## 模式 9: 撞 hard wall 还能继续 — 换文件 (6/4 新增)

**数据**: Phase 76-79 期间 sibling 在改 SessionDrawer + MainScreen (3-tabs 大重构)
**症状**: 以为没活干, 实际只是撞 sibling
**修复方案**:
1. 改别的文件 (ChatView, useHermesSnapshot, lib/pairCode, lib/discover)
2. Phase 70 PHASES.md 后, backlog 可以按文件分类
3. 撞 sibling 不一定是 end, 是"换个文件"

## 模式 10: 假设上游没实现 — 实际有 (6/4 新增)

**数据**: 假设 "hermes-agent 没 pair 协议" → 实际 `gateway/pairing.py` 450 行 DM pairing
**症状**:
- 直接做"上游没有 X" 假设
- 实际做了 450 行
- 重复造 toy-grade (我 6 字符 Math.random vs 上游 8 字符 SHA-256)
**修复方案**:
1. 永远先 audit 上游 `ls /path` + `grep -rn X /path`
2. 大仓 (61 个 .py) 不 audit 就假设 = 撞墙
3. 上游有, 学上游; 上游没有, 借鉴上游的安全模式

## 模式 11: secret + bash heredoc + write_file 三重坑 (6/4 新增)

**数据**: Phase 79 期间 3 次撞同一类墙
**症状 1**: `Authorization: Bearer *** 在 bash heredoc 里被 glob 展开, curl 报"option ---: is unknown"
**症状 2**: write_file 看到 32 字符 hex 自动替换成 `***`
**症状 3**: 写到 .sh 文件里跑起来 key 是 `***` 字符串
**修复方案**:
1. 写 .sh 时 key 用 env var (`K="..."`) 单独一行, 不要 inline
2. 写完 `cat script.sh | head -3` 验证实际内容
3. 跑起来先 `bash -n script.sh` 语法检查, 再真跑
4. 用 `set -e` 早 fail

## 模式 12: Node test 不能拉 RN runtime (6/4 新增)

**数据**: discover.ts import isNarrow from utils/platform, 拉 react-native, esbuild 炸
**症状**: `tsx tests/smoke.test.ts` → "Unexpected 'typeof' at react-native/index.js:27"
**修复方案**:
1. util 模块用 `typeof window !== 'undefined' && window.innerWidth` 内联检测
2. 任何会被 Node test 引用的 module, 不能 import react-native
3. 用 universal guard (`typeof window/document/navigator`)

## 模式 13: Client-side 测 breaker 测不出来 (6/4 新增)

**数据**: Phase 79 写完 circuit breaker, 测 6 次 bad model 全 200 OK, breaker 不跳
**根因**: gateway 把 "unknown model" 当 "正常 empty response" 返回, 不 raise 异常
**修复方案**:
1. 测 breaker 要触发真正 raise 的状态 (timeout, 5xx, socket close)
2. 不能只看 happy path
3. 写完测试要真的触发"被保护的状态"

## 模式 14: 实现 flow 前先 verify server 端支持 (6/4 新增)

**数据**: Phase 78 客户端 6 字符 pair code, 上游没 `/api/pair/redeem`, 整个 flow 是断的
**症状**:
- 写客户端走完 happy path
- 真用户跑起来发现 server 不支持
- 整个 phase 推倒
**修复方案**:
1. 实现一个"flow"前, 先 `curl` 验证 server 端支持
2. 不支持就明确告诉用户"这个 flow 是 demo"
3. 别自己造 server 端 (那是 upstream, 你改不了)
