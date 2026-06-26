---
name: mimo-tts
description: Text-to-speech synthesis using mimo-v2.5-tts-voicedesign. Generates audio from text with custom voice design via natural language description. Use when the user wants to convert text to speech, generate audio, synthesize voice, or says "语音合成", "文字转语音", "TTS", "读这段话", "生成语音".
disable-model-invocation: true
---

# mimo-v2.5-tts-voicedesign 语音合成

使用小米 mimo-v2.5-tts-voicedesign 模型，通过自然语言描述定制音色，将文本转为语音。

## 配置文件

脚本从 skill 目录下的 `.env` 文件读取配置，也可通过系统环境变量覆盖。

```
MIMO_API_KEY=your_api_key
MIMO_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1
```

若 `.env` 不存在或缺少字段，脚本会报错并提示用户创建。

## 参数

| 参数 | 说明 | 是否必填 | 默认值 |
|------|------|----------|--------|
| 音色描述 | 放在 `user` 消息中，自然语言描述目标音色 | 是 | - |
| 合成文本 | 放在 `assistant` 消息中，要转为语音的文本 | 是 | - |
| output_path | 音频文件保存路径 | 否 | `./output.wav` |
| optimize_text_preview | 设为 true 时模型自动润色播报文本 | 否 | `true` |

## Workflow

### 1. 确认输入

向用户确认两个内容：
- **合成文本**：需要转为语音的文字内容
- **音色描述**：用自然语言描述想要的声音（如不确定，参考 references/voice-prompt-guide.md 给出建议）

输出路径若用户未指定，默认为当前目录下 `./output.wav`。

### 2. 构建请求

调用脚本执行合成：

```bash
uv run skills/mimo-tts/scripts/tts.py \
  --voice-prompt "音色描述" \
  --text "合成文本" \
  --output "输出路径"
```

可选参数：
- `--no-optimize`：关闭文本自动润色（默认开启）

### 3. 输出结果

脚本成功后，告知用户实际保存的音频文件绝对路径。

## 音色描述快速指南

核心维度（1-4句即可）：

- **性别与年龄**：如"二十多岁的年轻女性"、"a middle-aged man"
- **音色质感**：如"温柔细腻"、"deep and raspy"
- **情绪语气**：如"沉稳自信"、"cheerful and energetic"
- **语速节奏**：如"语速偏慢"、"speaks quickly"

完整技巧见 references/voice-prompt-guide.md。

## 常见错误排查

1. **MIMO_API_KEY 未设置**：提示用户在环境变量中配置
2. **输出目录不存在**：脚本会自动创建
3. **合成文本过长**：建议单次不超过 500 字，长文本分段合成

## Resources

- 音色描述详细指南：references/voice-prompt-guide.md
