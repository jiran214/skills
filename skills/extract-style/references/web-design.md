# 网页风格提取最佳实践

## 工具

使用 playwright-cli 操作截取完整页面。

### 截图流程

**禁止直接用 `--full-page`**，现代网页多用内部滚动容器，fullPage 只能截首屏。

1. `playwright-cli snapshot` 识别滚动容器
2. 分段 `eval` 设置 `scrollTop`，每段截一张视口图
3. 用 sharp/Jimp/Pillow 拼接，重叠区域裁 50px

**关键**：不修改 CSS，顺着滚动机制走。

- `TimeoutError` 时：重启会话：`playwright-cli close` → `open`
- 用 run-code：`playwright-cli run-code "async (page) => { await page.screenshot({ path: 'x.png', timeout: 60000 }); return 'done'; }"`

## 分析维度

分析网页风格时，重点关注以下维度的**偏离默认值**选择：

### 1. 色彩系统

| 观察点 | 问自己 |
|--------|--------|
| 主色调 | 是否偏离科技蓝/安全绿等常见选择？ |
| 色彩数量 | 用了几种颜色？是否刻意克制？ |
| 渐变使用 | 有渐变吗？是多色渐变还是单色深浅？ |
| 强调色 | CTA按钮用什么色？出现频率如何？ |
| 黑白占比 | 灰度内容占多大比例？ |

**常见偏差模式：**
- 极简单色（如纯黑白+一个强调色）
- 暗色主题（dark-first）
- 渐变色（双色/多色渐变）
- 高饱和撞色
- 低饱和莫兰迪色系

### 2. 排版

| 观察点 | 问自己 |
|--------|--------|
| 字体选择 | 衬线/无衬线/混搭？中英文字体组合？ |
| 字号层级 | 标题与正文的倍率关系？ |
| 字重使用 | 常规/粗体/细体的分布？ |
| 行高与字间距 | 偏松还是偏紧？ |
| 对齐方式 | 左对齐/居中/右对齐/混合？ |

**常见偏差模式：**
- 超大标题（hero section 标题占屏幕 30%+）
- 极细字重（传递轻盈感）
- 紧凑排版（高信息密度）
- 大量留白（低信息密度）

### 3. 布局结构

| 观察点 | 问自己 |
|--------|--------|
| 网格系统 | 几列布局？是否打破常规网格？ |
| 留白比例 | 内容区与空白的比例？ |
| 内容密度 | 首屏信息量大小？ |
| 视觉流向 | F型/Z型/中心辐射？ |

**常见偏差模式：**
- 全屏hero（一屏一个焦点）
- 卡片网格（信息聚合）
- 单列长滚动（叙事性）
- 不对称布局（打破平衡）

### 4. 视觉元素

| 观察点 | 问自己 |
|--------|--------|
| 图形风格 | 扁平/3D/线框/点阵/手绘？ |
| 图标风格 | 线性/填充/双色调？ |
| 图片处理 | 圆角/直角/裁切方式？滤镜风格？ |
| 装饰元素 | 有无背景纹理/光效/阴影？ |

**常见偏差模式：**
- 线框/描边风格（轻量感）
- 点阵/像素风格（科技感/复古感）
- 毛玻璃/模糊（depth感）
- 几何抽象图形
- 纯文字排版（无图片依赖）

### 5. 动效与交互

| 观察点 | 问自己 |
|--------|--------|
| 过渡效果 | 页面切换/元素出现的方式？时长、缓动曲线？ |
| 滚动效果 | 视差/固定/渐显？触发方式？ |
| 悬停状态 | 按钮/卡片的hover反馈？过渡效果？ |
| 加载体验 | skeleton/进度条/动画？ |
| 动画实现方式 | CSS动画/JS动画/混合？ |
| 滚动驱动动画 | Intersection Observer/scroll-timeline/视差库？ |
| 3D/WebGL效果 | CSS 3D transforms/Three.js/Babylon.js？ |
| 微交互细节 | spring/ease曲线类型？stagger延迟？magnetic hover？ |

**常见偏差模式：**
- 无动效（静态、快速）
- 微交互（微妙的反馈）
- 沉浸式滚动（视差+渐显叙事）
- 物理模拟（弹性、惯性）
- 弹簧动画（spring physics）
- 视差滚动（parallax scrolling）
- 滚动触发渐显（scroll-triggered fade-in）
- 磁性悬停（magnetic hover）
- 3D变换（CSS 3D transforms）
- WebGL/Three.js效果

### 6. 组件风格

| 观察点 | 问自己 |
|--------|--------|
| 按钮样式 | 实心/描边/幽灵？圆角大小？ |
| 卡片样式 | 有无边框？阴影深度？圆角？ |
| 输入框 | 边框风格？聚焦状态？ |
| 导航 | 顶部/侧边/汉堡菜单？ |

### 7. 技术框架识别

| 观察点 | 问自己 |
|--------|--------|
| 前端框架 | React/Vue/Angular/Svelte/Next.js/Nuxt/Astro？ |
| CSS方案 | Tailwind/CSS Modules/Styled Components/BEM/原生CSS？ |
| 动画库 | GSAP/Framer Motion/Anime.js/Lottie/Three.js/原生CSS动画？ |
| UI组件库 | shadcn/ui/Ant Design/Material UI/Chakra UI/Radix？ |
| 构建工具 | Vite/Webpack/Next.js/Nuxt/Astro？ |

**识别线索：**
- **DOM结构**：React使用`data-reactroot`、Vue使用`data-v-`属性
- **class命名**：Tailwind使用原子类、CSS Modules使用哈希类名、BEM使用`block__element--modifier`
- **script标签**：查看引入的JS文件和全局变量
- **数据属性**：框架特有的数据属性（如`data-testid`、`data-qa`）
- **样式标签**：Styled Components生成带hash的`<style>`标签

### 8. 代码层面分析（通过Playwright evaluate）

**提取内容：**
- CSS变量：从`:root`或`<style>`标签提取自定义属性
- 计算样式：提取关键元素的fontSize、fontWeight、lineHeight、color、backgroundColor、padding、margin、borderRadius等
- 动画库：检测gsap、framer-motion、three、lottie、anime等全局变量
- CSS动画：遍历样式表提取`@keyframes`定义
- 框架特征：检测React、Vue、Angular、Svelte、Next.js、Nuxt、Astro的特征属性

## 输出格式规范

输出风格系统时，使用以下结构化格式：

### 1. 核心风格偏差

```markdown
## 风格定义
- **核心理念**：一句话描述风格的核心
- **偏差量**：在哪些维度上偏离了默认值
- **适用场景**：这种风格适合什么类型的项目

## 偏差分析
### 视觉维度
- 色彩：[具体偏差]
- 排版：[具体偏差]
- 布局：[具体偏差]
- 视觉元素：[具体偏差]
- 动效：[具体偏差]
- 组件：[具体偏差]

### 技术维度
- 框架选择：[具体偏差]
- CSS方案：[具体偏差]
- 动画实现：[具体偏差]
```

### 2. Design Token 清单

```markdown
## Design Tokens
### 颜色
- 主色：#hex
- 辅助色：#hex
- 强调色：#hex
- 背景色：#hex
- 文本色：#hex

### 字体
- 标题字体：font-family
- 正文字体：font-family
- 字号层级：[具体值]

### 间距
- 基础单位：Xpx
- 组件间距：[具体值]
- 页面边距：[具体值]

### 圆角
- 小圆角：Xpx
- 中圆角：Xpx
- 大圆角：Xpx
```

### 3. 动画参数

```markdown
## 动画参数
### 时长
- 快速过渡：Xms
- 标准过渡：Xms
- 慢速过渡：Xms

### 缓动曲线
- 标准：cubic-bezier(...)
- 弹性：cubic-bezier(...)
- 减速：cubic-bezier(...)

### 滚动动画
- 触发方式：[Intersection Observer/scroll-timeline/库]
- 视差强度：[具体值]
- 渐显效果：[具体描述]

### 微交互
- 悬停效果：[具体描述]
- 点击反馈：[具体描述]
- 加载状态：[具体描述]
```

### 4. 组件变体

```markdown
## 组件规范
### 按钮
- 主要按钮：[样式描述]
- 次要按钮：[样式描述]
- 幽灵按钮：[样式描述]
- 禁用状态：[样式描述]

### 卡片
- 基础卡片：[样式描述]
- 悬停状态：[样式描述]
- 选中状态：[样式描述]

### 输入框
- 默认状态：[样式描述]
- 聚焦状态：[样式描述]
- 错误状态：[样式描述]
```

### 5. 技术栈信息

```markdown
## 技术栈
### 前端框架
- 主要框架：[框架名称]
- 版本：[版本号]
- 关键特征：[识别到的特征]

### CSS方案
- 方案类型：[Tailwind/CSS Modules/Styled Components/BEM/原生CSS]
- 关键特征：[识别到的特征]

### 动画库
- 使用的库：[库名称]
- 实现方式：[CSS动画/JS动画/混合]
- 关键特征：[识别到的特征]

### UI组件库
- 使用的库：[库名称]
- 关键特征：[识别到的特征]
```