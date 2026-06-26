# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "openai>=1.0.0",
#     "numpy",
#     "soundfile",
# ]
# ///
"""mimo-v2.5-tts-voicedesign 语音合成脚本"""

import argparse
import base64
import os
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from openai import OpenAI


def load_env(env_path: Path) -> dict[str, str]:
    """从 .env 文件加载环境变量"""
    config = {}
    if not env_path.exists():
        return config
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            config[key.strip()] = value.strip().strip('"').strip("'")
    return config


def main():
    parser = argparse.ArgumentParser(description="mimo-v2.5-tts-voicedesign 语音合成")
    parser.add_argument("--voice-prompt", required=True, help="音色描述，自然语言描述目标音色")
    parser.add_argument("--text", required=True, help="要合成的文本")
    parser.add_argument("--output", default="./output.wav", help="输出文件路径 (默认: ./output.wav)")
    parser.add_argument("--no-optimize", action="store_true", help="关闭文本自动润色")
    args = parser.parse_args()

    # 从 skill 目录下的 .env 文件读取配置
    skill_dir = Path(__file__).resolve().parent.parent
    env_path = skill_dir / ".env"
    env = load_env(env_path)

    api_key = env.get("MIMO_API_KEY") or os.environ.get("MIMO_API_KEY")
    base_url = env.get("MIMO_BASE_URL") or os.environ.get("MIMO_BASE_URL")

    if not api_key or not base_url:
        print(f"错误: 缺少 MIMO_API_KEY 或 MIMO_BASE_URL", file=sys.stderr)
        print(f"请在 {env_path} 中配置:", file=sys.stderr)
        print(f"  MIMO_API_KEY=your_api_key", file=sys.stderr)
        print(f"  MIMO_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url=base_url)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    messages = [
        {"role": "user", "content": args.voice_prompt},
        {"role": "assistant", "content": args.text},
    ]

    audio_config = {
        "format": "wav",
        "optimize_text_preview": not args.no_optimize,
    }

    try:
        completion = client.chat.completions.create(
            model="mimo-v2.5-tts-voicedesign",
            messages=messages,
            audio=audio_config,
        )

        message = completion.choices[0].message
        audio_bytes = base64.b64decode(message.audio.data)

        with open(output_path, "wb") as f:
            f.write(audio_bytes)

        print(f"音频已保存到: {output_path.resolve()}")

    except Exception as e:
        print(f"合成失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
