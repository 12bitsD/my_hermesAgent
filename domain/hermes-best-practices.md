# Hermes 使用最佳实践

> 从历史 session 中提炼的经验
> 最后更新: 2026-06-03

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
