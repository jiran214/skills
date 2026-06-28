---
name: extract-style
description: Extract the style system from any work — images, text, music, games, video, UI, architecture, or a creator's body of work. Use when the user says "extract style", "分析风格", "提取风格", "style guide", "风格系统", "风格拆解", or wants to understand what makes a work look/feel a certain way.
disable-model-invocation: true
---

# 风格提取

从任意作品中提取可复用的风格系统。

## 本质

风格 = 一组稳定的选择偏好和约束规则，使作品在感知上形成可识别的一致性。

核心是找到那些让作品"不一样"的**偏差**，而不是穷举所有特征。

## 原则

- **只提取偏离默认值的选择**：模型已经知道什么是常规做法，不需要你告诉它
- **风格 = 偏差量**：这个作品在哪些维度上选择了与众不同的路径
- **面向生成**：提取的规则要能用于 AI 生成类似风格的作品
- **风格是形式，不是内容**：只关注"怎么呈现"

## Workflow

1. 确定输入：单个作品 → 提取该作品风格；多个作品 → 提取共性风格（创作者/项目风格）

2. 识别作品类型（如：网页、UI、品牌、插画、摄影、排版、游戏、建筑等）

3. 检查 references/ 目录是否有该类型的最佳实践文件：
   - 文件命名格式：`{类型}.md`（如 `web-design.md`、`ui-design.md`）
   - 如果存在，读取该文件作为分析框架参考
   - 如果不存在，基于通用原则进行分析

4. 技术层面分析（仅限可交互作品）：
   - 识别技术框架和实现方式（如适用）
   - 通过 Playwright evaluate 提取代码层面信息
   - 分析技术实现对风格的影响

5. 分析：结合类型最佳实践（如有），找出该风格最核心的选择偏差

6. 输出风格系统
