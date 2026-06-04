# Hermes 使用最佳实践

> 从历史 session 中提炼的经验
> 最后更新: 2026-06-04 (Phase 79 撞墙后追加)

## 开发流程

### 修改-验证循环（最可靠）
```
1. read_file 确认目标内容
2. patch 修改代码
3. tsc --noEmit (TypeScript) 或 npm run build (其他)
4. browser_vision 查看实际效果
5. 如果有问题 → 回到步骤 1
6. 如果没问题 → 继续下一个修改
```

### 渐进式提交
```
功能完成 → git add src/ → git commit -m "feat: xxx" → git push
```
不要攒一堆改动再提交。小步快跑。

### 意图对齐检查（每 5-10 turn）
自问：
1. 我还在做用户要的东西吗？
2. 我的方向对吗？
3. 用户的需求变了吗？
4. 还有哪些待办没完成？
5. **我还考虑过 "新用户" 吗?** (撞墙 #5, 5 维饱和 ≠ 没活干)

## Git 操作

### Commit 规范
```
feat: 新功能
fix: 修复
refactor: 重构
docs: 文档
chore: 杂项
```

### 自动 push
- 用户已明确授权: "可以直接提交push"
- 每完成一个功能点就 push
- 不需要每次询问用户

## 错误处理

### LSP 假报错
- LSP cache 多文件 patch 后会报 stale syntax 错
- **判断标准**: tsc --noEmit 干净就是真 OK
- 不要被 LSP 红线误导

### Tool Error
- 立即分析原因，不要继续执行
- 常见: patch 找不到目标字符串（内容已被修改）
- 修复: 重新 read_file 确认当前内容

### Context Compaction
- 长 session 会触发 context compaction
- compaction 后可能丢失原始意图
- 修复: 读取项目的 CONTEXT.md 恢复上下文

## 自主模式

### 核心原则
- "不叫停就不停"
- phase 完成 → commit+push → 下一 phase
- 只有撞硬墙（账号/外部 API/不可逆）才 ping 用户

### 汇报节奏
- 每完成一个功能点做简短汇报
- 格式: "已完成 X，正在进行 Y，下一步 Z"
- 不要长时间沉默

## 工具使用

### search_files vs read_file
- search_files: 找文件、搜内容（模糊匹配）
- read_file: 精确读取已知路径

### execute_code vs terminal
- execute_code: 需要循环、条件分支、多步处理
- terminal: 单条命令、git、npm、构建

### patch vs write_file
- patch: 精确替换已知内容
- write_file: 重写整个文件（谨慎使用）

## 跨仓库操作 (6/4 新增)

### 区分 upstream vs my-fork
**永远先** `git remote -v` 确认 origin 是你的, 还是上游:
- ✅ `git@github.com:12bitsD/xxx.git` (你的, 可 push)
- ❌ `git@github.com:NousResearch/xxx.git` (上游, 不能 push, 改了也白改)

**Rule**: 改 hermes-chat 适配 hermes-agent, 不反过来

### Revert 越界 commit
```
git reset --hard <last-good-commit-sha>
```
不要 amend 改 history. history 是事实, revert 是修正.

## 写脚本 / heredoc 注意事项 (6/4 新增)

### secret 不要 inline
**症状**: `Authorization: Bearer *** 出现 glob 展开, 后续 `=***` 啥的不是 flag
**症状 2**: write_file 看到 32 字符 hex 也替换成 `***`
**修复**: 用 env var:
```bash
K="5ba3863bd0be0c9d2de2b3eb1def16c3"
curl -H "Authorization: Bearer *** "$K
```
**验证**: 写完 `cat script.sh | head -3` 看实际内容

### bash heredoc + 复杂命令 → 写到 .sh
**症状**: 终端多行命令里 `(` `)` `done` `for` 容易 syntax error
**修复**: 写到 .sh 文件, `bash script.sh`, 容易 debug

## Node test 兼容性 (6/4 新增)

### 不能 import react-native
**症状**: `tsx tests/smoke.test.ts` → esbuild 失败 "Unexpected 'typeof' at react-native/index.js:27"
**原因**: util 模块里 `import { isNarrow } from 'utils/platform'` 拉了 RN 整个 runtime
**修复**: util 用 `typeof window !== 'undefined' && window.innerWidth` 内联检测
**Rule**: 任何会被 Node smoke test 引用的 module, 不能 import react-native. 只用 universal guard (`typeof window/document/navigator`)

## 发现上游已实现什么 (6/4 新增)

### 永远先 audit 上游
撞墙经验: 我假设 "hermes-agent 没 pair 协议" → 实际有 450 行 DM pairing.
**Lesson**: 任何"上游没有 X"的假设, 先 `ls /path` + `grep -rn X /path` 验证.
特别是大仓 (hermes-agent 61 个 .py), 不 audit = 撞墙.

### 借鉴上游的安全模式
hermes-agent `gateway/pairing.py` 的 8 字符 + SHA-256 + lockout + 0600 file 是
production-grade. 我自己的 Phase 78 客户端 6 字符 + Math.random 是 toy-grade.
**Rule**: 上游有什么, 先学上游, 再决定要不要自己造.

## 撞墙后处理 (6/4 新增)

### 撞"5 维饱和"墙
**症状**: 5 维都覆盖了, 觉得没活干
**真相**: 5 维全是开发者视角, 真实用户首次开 app 啥都不懂
**修复**: 加第 6 维 "onboarding completeness" (新用户能否 0 指导上手)

### 撞"撞墙撞墙"墙
**症状**: SessionDrawer + MainScreen 被 sibling 改, 我不能用
**修复**: 改别的文件 (ChatView, useHermesSnapshot, lib/pairCode, lib/discover)
**Lesson**: 撞 hard wall 不一定是"没活干", 也可以是"换个文件"

## Hermes API 知识 (6/4 新增)

### 客户端知道的事
- ✅ `/v1/health` (no auth, 200 OK)
- ✅ `/v1/models` (auth required)
- ✅ `/v1/chat/completions` (OpenAI-compatible, stream + non-stream)
- ✅ `/v1/capabilities` (model caps)
- ✅ `/v1/skills`, `/v1/toolsets`
- ✅ `/api/sessions` (CRUD)
- ✅ `/api/jobs` (cron jobs)
- ✅ X-Hermes-Session-Id / X-Hermes-Session-Key headers
- ❌ Device pair 路由 (没有, 别假设)
- ❌ /api/pair/redeem (没有)

### Hermes 永远在 127.0.0.1:8642 (Mac)
- 客户端默认 endpoint 应该是 `http://127.0.0.1:8642`
- 真实用户首次开 app, 不知道填啥 → 用 "Find my Hermes" auto-discover
- Phone 用户需要: 同一 WiFi (Mac IP) / Tailscale (.local) / Cloudflare tunnel
