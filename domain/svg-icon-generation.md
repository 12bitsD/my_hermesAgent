# Agent SVG Icon 生成最佳实践

> 最后更新: 2026-06-03

## 核心发现

SVG icon 生成对 Agent 来说是**天然友好**的任务 — 纯文本输出，不需要图片生成模型，
直接写代码就行。关键是掌握正确的模板和规范。

## 三种主流风格

### 1. Stroke-Based（Lucide/Feather 风格）— 最推荐
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" 
     viewBox="0 0 24 24" fill="none" stroke="currentColor" 
     stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
</svg>
```
- 优点: 简洁、易生成、currentColor 自动适配主题
- 适用: 大多数 UI icon 场景

### 2. Filled（Heroicons Solid 风格）
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" 
     viewBox="0 0 24 24" fill="currentColor">
  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10..."/>
</svg>
```
- 优点: 视觉冲击力强
- 适用: 底部 tab bar、强调状态

### 3. Duotone（Phosphor 风格）— 高级感
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" 
     viewBox="0 0 24 24" fill="currentColor">
  <path opacity="0.3" d="M12 22V12"/>  <!-- 次要层 -->
  <path d="M12 2L2 7l10 5 10-5-10-5z"/>  <!-- 主要层 -->
</svg>
```
- 优点: 层次感、设计感
- 适用: 需要区分主次信息的 icon

## Agent 生成 SVG 的 Prompt 模板

### 模板 1: 单个 Stroke Icon
```
生成一个 24x24 的 SVG icon，描述: [图标描述]
要求:
- viewBox="0 0 24 24"
- stroke-based: fill="none", stroke="currentColor"
- stroke-width="2", stroke-linecap="round", stroke-linejoin="round"
- 只用 <path> 元素
- 不要 inline style，不要注释
- 输出纯 SVG 代码
```

### 模板 2: 批量生成（Sprite Sheet）
```
生成一组 5 个相关 SVG icons: [列表]
每个 icon 必须:
- 使用相同的 base attributes
- 适配 24x24 网格，2px padding
- 视觉风格一致
输出为 <symbol> 元素，可用 sprite sheet 引用
```

## 工具链

### 优化: SVGO
```bash
npm install -g svgo
svgo icon.svg -o icon-optimized.svg
```
关键配置: 保留 viewBox，移除无用属性

### 验证清单
Agent 生成 SVG 后自检:
- [ ] 有 viewBox="0 0 24 24"
- [ ] 无 inline style
- [ ] 用 currentColor 支持主题
- [ ] 坐标在 0-24 范围内
- [ ] 无注释/metadata

## 与 Hermes Agent 的集成

### 方案 1: 直接生成（推荐）
Agent 直接在 write_file 中写 SVG 代码，无需额外工具。
适合: 单个 icon、简单图标

### 方案 2: 模板 + 参数化
```javascript
function createStrokeIcon(paths, options = {}) {
  const { size = 24, strokeWidth = 2 } = options;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" 
    viewBox="0 0 ${size} ${size}" fill="none" stroke="currentColor" 
    stroke-width="${strokeWidth}" stroke-linecap="round" stroke-linejoin="round">
    ${paths.map(d => `  <path d="${d}"/>`).join('\n')}
  </svg>`;
}
```

### 方案 3: 参考现有 icon 库
- Lucide: https://lucide.dev (stroke-based, 24x24)
- Phosphor: https://phosphoricons.com (6 种粗细)
- Heroicons: https://heroicons.com (outline + solid)

## 常见错误

| 错误 | 修复 |
|------|------|
| 缺少 xmlns | 始终包含 xmlns="http://www.w3.org/2000/svg" |
| 没有 viewBox | 始终指定 viewBox="0 0 24 24" |
| 用 style="" | 用属性代替 (fill, stroke 等) |
| 硬编码颜色 | 用 currentColor 支持主题 |
| 复杂 transform | 简化为基本 path 坐标 |
