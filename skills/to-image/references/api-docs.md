# Agnes Image 2.1 Flash API 详细文档

## API 信息

- **Base URL**: `https://apihub.agnes-ai.com`
- **Endpoint**: `https://apihub.agnes-ai.com/v1/images/generations`
- **请求方法**: POST
- **Content-Type**: application/json
- **认证方式**: Bearer Token

## 认证 Header

```
Authorization: Bearer YOUR_API_KEY
```

API Key 从环境变量 `AGNES_API_KEY` 读取。

## 请求参数完整列表

| 参数 | 类型 | 是否必填 | 说明 |
|------|------|----------|------|
| `model` | string | 是 | 模型名称，固定 `agnes-image-2.1-flash` |
| `prompt` | string | 是 | 图片生成或编辑提示词 |
| `size` | string | 是 | 输出图片尺寸，例如 `1024x768` |
| `image` | string[] | 图生图必填 | 输入图片数组，支持公网 URL 或 Data URI Base64 |
| `return_base64` | boolean | 否 | 文生图需要返回 Base64 时使用 |
| `extra_body` | object | 否 | 高级工作流扩展参数 |
| `extra_body.response_format` | string | 否 | 输出格式：`url` 或 `b64_json` |

## 请求示例

### 1. 文生图 - URL 输出

```bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-image-2.1-flash",
    "prompt": "A luminous floating city above a misty canyon at sunrise, cinematic realism",
    "size": "1024x768",
    "extra_body": {
      "response_format": "url"
    }
  }'
```

### 2. 文生图 - Base64 输出

```bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-image-2.1-flash",
    "prompt": "A clean product photo of a glass cube on a white studio background, soft shadows, high detail",
    "size": "1024x768",
    "return_base64": true
  }'
```

### 3. 图生图 - URL 输入，URL 输出

```bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-image-2.1-flash",
    "prompt": "Transform the scene into a rain-soaked cyberpunk night with neon reflections while preserving the original composition",
    "size": "1024x768",
    "extra_body": {
      "image": ["https://example.com/input-image.png"],
      "response_format": "url"
    }
  }'
```

### 4. 图生图 - URL 输入，Base64 输出

```bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-image-2.1-flash",
    "prompt": "Make the object orange while preserving the original composition",
    "size": "1024x768",
    "extra_body": {
      "image": ["https://example.com/input-image.png"],
      "response_format": "b64_json"
    }
  }'
```

### 5. 图生图 - Data URI Base64 输入

```bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-image-2.1-flash",
    "prompt": "Make the object matte black while preserving the original composition",
    "size": "1024x768",
    "extra_body": {
      "image": ["data:image/png;base64,BASE64_HERE"],
      "response_format": "b64_json"
    }
  }'
```

## 返回格式

### URL 输出

```json
{
  "created": 1780000000,
  "data": [
    {
      "url": "https://storage.googleapis.com/agnes-aigc/xxx.png",
      "b64_json": null,
      "revised_prompt": null
    }
  ]
}
```

生成图片 URL：`data[0].url`

### Base64 输出

```json
{
  "created": 1780000000,
  "data": [
    {
      "url": null,
      "b64_json": "iVBORw0KGgoAAAANSUhEUgAA...",
      "revised_prompt": null
    }
  ]
}
```

生成图片 Base64：`data[0].b64_json`

## 核心能力

| 能力 | 说明 |
|------|------|
| 文生图 | 根据自然语言提示词生成高质量图片 |
| 图生图 | 根据提示词对已有图片进行转换、编辑或优化 |
| 高信息密度图像优化 | 更好处理复杂布局、丰富细节和密集视觉元素 |
| 构图保持 | 图生图时可尽量保持原图构图、主体结构和视角 |
| 灵活尺寸控制 | 支持自定义输出尺寸 |
| URL 返回 | 支持将生成结果以可访问图片 URL 返回 |
| Base64 返回 | 支持将生成结果以 Base64 数据返回 |

## 适用场景

- 创意设计：概念图、视觉探索、海报草图
- 营销内容：活动图、产品视觉、社交媒体素材
- 高密度视觉生成：复杂场景、丰富构图、密集元素画面
- 图片转换：风格迁移、场景重打光、背景转换
- 内容生产：App 素材、缩略图、Banner
- 产品视觉：产品图、展示图、商业视觉

## 价格

$0.003 / 张

## 注意事项

1. 模型名称固定使用 `agnes-image-2.1-flash`
2. `response_format` 必须放在 `extra_body` 中，不能放在顶层
3. 图生图不需要传 `tags: ["img2img"]`
4. 输入图片 URL 必须公网可访问
5. 建议客户端超时时间：60s ~ 360s
