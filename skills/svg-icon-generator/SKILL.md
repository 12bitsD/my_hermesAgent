---
name: svg-icon-generator
description: "生成高质量 SVG icon：描述 → 生成 → 自检 → 优化 → 输出。支持 Anthropic 风格（渐变填充、温暖中性色、细描边、柔和圆角）和 Lucide 风格（stroke-based）。"
version: 2.0.0
metadata:
  hermes:
    tags: [svg, icon, design, ui, generation, anthropic]
    config:
      - key: svg_icon.style
        description: 默认风格 (anthropic/lucide/filled/duotone)
        default: "anthropic"
      - key: svg_icon.size
        description: 默认尺寸
        default: "24"
---

# SVG Icon Generator

> Agent 专用 SVG icon 生成工作流
> 描述 → 生成 → 自检 → 优化 → 输出

## 风格选择

### ⭐ Anthropic 风格（默认，推荐）
温暖中性色 + 渐变填充 + 细描边 + 柔和圆角
适用: 高级感、友好、专业的 UI

### Lucide 风格
stroke-based + currentColor + 2px 描边
适用: 简洁、可主题适配的 icon

### Filled 风格
纯色填充 + currentColor
适用: tab bar、状态强调

### Duotone 风格
主次层分离 + opacity 区分
适用: 需要层次感的 icon

## Anthropic 风格模板

### 色板
```
暖米色: #d4a574 → #c4956a
暖金色: #e8c170 → #d4a574
珊瑚色: #e8a0a0 → #d48080
琥珀色: #f0c060 → #e8a040
鼠尾草: #a0c4a0 → #80a480
石板蓝: #a0a4c4 → #8084a4
赤陶色: #d4a080 → #c48060
```

### 生成模板
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{light_color};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{dark_color};stop-opacity:1" />
    </linearGradient>
  </defs>
  <path d="{path_data}" 
        fill="url(#grad)" stroke="{stroke_color}" stroke-width="0.5"/>
</svg>
```

### 设计规则
1. **渐变方向**: 从左上到右下 (x1="0%" y1="0%" x2="100%" y2="100%")
2. **描边**: 0.5px，颜色比填充深 20%
3. **圆角**: 所有形状使用圆角
4. **避免**: 高饱和度颜色、纯色填充、尖锐边角

## Lucide 风格模板

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" 
     viewBox="0 0 24 24" fill="none" stroke="currentColor" 
     stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="{path_data}"/>
</svg>
```

## 生成流程

### Step 1: 理解需求
- 确认 icon 描述（什么物体/动作/概念）
- 确认风格（anthropic/lucide/filled/duotone）
- 确认用途（tab bar/按钮/装饰）

### Step 2: 选择色板
根据 icon 含义选择色板:
- Chat/沟通 → 暖米色 (#d4a574)
- Star/评价 → 暖金色 (#e8c170)
- Heart/喜欢 → 珊瑚色 (#e8a0a0)
- Lightning/快速 → 琥珀色 (#f0c060)
- Shield/安全 → 鼠尾草 (#a0c4a0)
- Code/技术 → 石板蓝 (#a0a4c4)
- Rocket/启动 → 赤陶色 (#d4a080)

### Step 3: 生成 SVG
使用对应风格的模板，填入路径数据。

### Step 4: 自检清单
生成后立即检查:
- [ ] viewBox="0 0 24 24" ✓
- [ ] 有 defs + linearGradient ✓ (Anthropic 风格)
- [ ] 描边 0.5px ✓ (Anthropic 风格)
- [ ] 颜色在色板范围内 ✓
- [ ] 无 inline style ✓
- [ ] 坐标在 0-24 范围 ✓

### Step 5: 输出
- 输出纯 SVG 代码（不加解释）
- 如果需要预览，写入文件用浏览器打开

## 路径生成技巧

### 基本形状
- 圆: `<circle cx="12" cy="12" r="10"/>`
- 矩形: `<rect x="4" y="4" width="16" height="16" rx="2"/>`
- 线: `<line x1="4" y1="12" x2="20" y2="12"/>`

### 常用 path 命令
- M x y: 移动到
- L x y: 画线到
- H x: 水平线
- V y: 垂直线
- A rx ry rotation large-arc sweep x y: 弧线
- Z: 闭合路径

### 24x24 网格参考
```
0   4   8   12  16  20  24
├───┼───┼───┼───┼───┼───┤
│       │       │       │  0-4: 边距
│   ┌───┼───┼───┼───┐   │  4-20: 内容区
│   │   │   │   │   │   │
│   │   │   ●   │   │   │  中心: (12,12)
│   │   │   │   │   │   │
│   └───┼───┼───┼───┘   │
│       │       │       │
├───┼───┼───┼───┼───┼───┤
```
- 内容区: 4-20（留 2px padding）
- 中心: (12, 12)
- 对称轴: x=12, y=12

## 参考资源

- Anthropic 设计风格: 温暖中性色、渐变、柔和圆角
- Lucide Icons: https://lucide.dev (stroke 风格参考)
- Phosphor Icons: https://phosphoricons.com (duotone 参考)
- Heroicons: https://heroicons.com (filled 参考)
