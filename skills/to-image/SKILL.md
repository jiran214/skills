---
name: to-image
description: Generate images using Agnes Image 2.1 Flash API. Supports text-to-image (文生图) and image-to-image (图生图). Use when the user wants to generate, create, edit, transform images, or says "生成图片", "画一个", "图片风格转换".
disable-model-invocation: true
---

# Agnes Image 2.1 Flash 图片生成

使用 Agnes Image 2.1 Flash API 生成或编辑图片。

## 环境变量

API Key 读取环境变量 `AGNES_API_KEY`，若未设置则提示用户配置。

## 参数说明

### 必填参数（文生图）
- `model`: 固定 `agnes-image-2.1-flash`
- `prompt`: 图片生成提示词
- `size`: 输出尺寸，如 `1024x768`

### 必填参数（图生图）
- 以上三个参数 + `image` 数组（放在 `extra_body` 中）

### 可选参数
- `return_base64`: boolean，文生图需要 Base64 输出时使用
- `extra_body.response_format`: `url` 或 `b64_json`，控制输出格式

## Workflow

### 1. 判断任务类型
- 用户提供文字描述 → 文生图
- 用户提供图片路径/URL + 编辑要求 → 图生图

### 2. 准备请求参数

**文生图请求体：**
```json
{
  "model": "agnes-image-2.1-flash",
  "prompt": "用户提示词",
  "size": "1024x768",
  "extra_body": {
    "response_format": "url"
  }
}
```

**图生图请求体：**
```json
{
  "model": "agnes-image-2.1-flash",
  "prompt": "编辑提示词",
  "size": "1024x768",
  "extra_body": {
    "image": ["图片URL或Base64"],
    "response_format": "url"
  }
}
```

### 3. 处理本地图片（图生图）

若用户提供本地图片路径，需转换为 Base64：

```bash
# 转换为 Data URI 格式
MIME_TYPE=$(file --mime-type -b "图片路径")
BASE64_DATA=$(base64 -i "图片路径")
echo "data:${MIME_TYPE};base64,${BASE64_DATA}"
```

将结果放入 `extra_body.image` 数组中。

### 4. 发送请求

```bash
curl -s https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '请求体JSON'
```

超时建议：120秒

### 5. 处理响应

- URL 输出：从 `data[0].url` 获取图片链接
- Base64 输出：从 `data[0].b64_json` 解码保存为文件

## 提示词技巧

### 文生图推荐结构
`[主体] + [场景/环境] + [风格] + [光照] + [构图] + [质量要求]`

示例：
```
A luminous floating city above a misty canyon at sunrise, cinematic realism, wide-angle composition, rich architectural details, soft golden light, high visual density
```

### 图生图推荐结构
`[修改要求] + [新风格/新场景] + [需要添加或移除的元素] + [需要保留的元素]`

示例：
```
Transform the scene into a rain-soaked cyberpunk night with neon reflections while preserving the original composition and main subject layout
```

### 高信息密度图片
明确描述视觉层级：主体、背景环境、次要元素、风格光照、构图约束。

## 常见错误排查

1. **response_format 放在顶层导致 400 错误**
   - 必须放在 `extra_body` 中

2. **图生图不需要 tags**
   - 不要传 `tags: ["img2img"]`

3. **输入图片 URL 不可访问**
   - 使用公网可访问的 HTTPS 地址
   - 或改用 Data URI Base64 输入

4. **请求超时**
   - 设置客户端超时 60s-360s

## Resources

- 详细 API 文档：references/api-docs.md
- 价格：$0.003/张
