"""
火山引擎（豆包语音）TTS 调用模块
====================================

负责与火山引擎 openspeech API 交互，将文本合成为语音音频。
支持：
- 单句合成（返回 bytes）
- 多音色试听（返回多个音色的试听片段）
- 情感参数控制（针对 emo_v2 系列音色）
- 速度/音调调节

API 文档参考:
  https://www.volcengine.com/docs/6561/1257544

认证方式:
  HTTP Header: X-Api-Key
"""

import json
import uuid
import logging
import requests
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────

# 火山引擎 TTS 非流式合成端点
VOLCANO_TTS_URL = "https://openspeech.bytedance.com/api/v1/tts"

# 火山方舟 Agent Plan 专属 TTS 端点（seed-tts-2.0）
VOLCANO_TTS_PLAN_URL = "https://openspeech.bytedance.com/api/v3/plan/tts/unidirectional"
VOLCANO_TTS_PLAN_RESOURCE_ID = "seed-tts-2.0"

# 推荐的治愈/故事类女声音色（按适用度排序）
RECOMMENDED_VOICES = {
    "甜美桃子":       "zh_female_tianmeitaozi_mars_bigtts",
    "柔美女友":       "zh_female_roumeinvyou_emo_v2_mars_bigtts",
    "魅力女友":       "zh_female_meilinvyou_emo_v2_mars_bigtts",
    "爽快思思":       "zh_female_shuangkuaisisi_emo_v2_mars_bigtts",
    "Vivi 2.0":       "zh_female_vv_uranus_bigtts",
    "小何 2.0":       "zh_female_xiaohe_uranus_bigtts",
    "俏皮女声 2.0":   "zh_female_qiaopinv_uranus_bigtts",
}


@dataclass
class VolcanoConfig:
    """火山引擎 TTS 调用配置"""
    app_id: str
    api_key: str
    cluster_id: str = "volcano_tts"
    voice_type: str = "zh_female_tianmeitaozi_mars_bigtts"
    # 语速：0.5 ~ 2.0，1.0 为正常，< 1.0 更慢
    speed_ratio: float = 1.0
    # 音量：0.5 ~ 2.0
    volume_ratio: float = 1.0
    # 音调：0.5 ~ 2.0
    pitch_ratio: float = 1.0
    # 输出格式
    encoding: str = "mp3"
    sample_rate: int = 24000
    # 情感控制（仅 emo_v2 系列音色支持）
    emotion: str = ""           # 如 "happy", "sad", "gentle"
    emotion_scale: float = 1.0  # 情感强度 0.1 ~ 10.0
    # Agent Plan 模式：api_key 以 'ark-' 开头时自动启用
    use_agent_plan: bool = False


# ──────────────────────────────────────────────────────────────
# 核心合成函数
# ──────────────────────────────────────────────────────────────

def synthesize_text(text: str, config: VolcanoConfig) -> bytes:
    """
    调用火山引擎 TTS API 合成单段文本。

    Args:
        text:   要合成的文本（建议单句，不超过 300 字）
        config: 火山引擎配置

    Returns:
        合成音频的二进制数据 (mp3/wav/pcm)

    Raises:
        RuntimeError: API 调用失败时
    """
    if not text.strip():
        raise ValueError("合成文本不能为空")

    # 构建请求体
    request_id = str(uuid.uuid4())

    # 判断是否使用 Agent Plan 模式
    # api_key 以 'ark-' 开头，或显式设置 use_agent_plan
    is_plan = config.use_agent_plan or config.api_key.startswith("ark-")

    if is_plan:
        # ── Agent Plan v3 模式 ──
        # 使用 X-Api-Key + X-Api-Resource-Id 鉴权
        # payload 使用 req_params 包裹，字段为 speaker（非 voice_type）
        url = VOLCANO_TTS_PLAN_URL
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": config.api_key,
            "X-Api-Resource-Id": VOLCANO_TTS_PLAN_RESOURCE_ID,
        }
        payload = {
            "req_params": {
                "reqid": request_id,
                "text": text,
                "text_type": "plain",
                "speaker": config.voice_type,
                "audio_config": {
                    "sample_rate": config.sample_rate,
                    "format": config.encoding,
                },
            }
        }
        # Agent Plan v3 的语速/音量/音调通过 audio_config 传递
        if config.speed_ratio != 1.0:
            payload["req_params"]["audio_config"]["speed_ratio"] = config.speed_ratio
        if config.volume_ratio != 1.0:
            payload["req_params"]["audio_config"]["volume_ratio"] = config.volume_ratio
        if config.pitch_ratio != 1.0:
            payload["req_params"]["audio_config"]["pitch_ratio"] = config.pitch_ratio

        logger.debug(f"[Volcano TTS] Agent Plan 模式: speaker={config.voice_type}, "
                     f"text={text[:30]}..., reqid={request_id}")
    else:
        # ── 传统 v1 模式 ──
        url = VOLCANO_TTS_URL
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer;{config.api_key}",
        }
        payload = {
            "app": {
                "appid": config.app_id,
                "token": "access_token",
                "cluster": config.cluster_id,
            },
            "user": {
                "uid": "tts-voiceover-skill",
            },
            "audio": {
                "voice_type": config.voice_type,
                "encoding": config.encoding,
                "speed_ratio": config.speed_ratio,
                "volume_ratio": config.volume_ratio,
                "pitch_ratio": config.pitch_ratio,
            },
            "request": {
                "reqid": request_id,
                "text": text,
                "text_type": "plain",
                "operation": "query",
            },
        }
        logger.debug(f"[Volcano TTS] v1 模式: voice={config.voice_type}, "
                     f"text={text[:30]}..., reqid={request_id}")

    # 如果是 emo_v2 系列音色，添加情感参数（仅 v1 模式有效）
    if not is_plan and config.emotion and "emo" in config.voice_type:
        payload["audio"]["emotion"] = config.emotion
        payload["audio"]["emotion_scale"] = config.emotion_scale

    try:
        resp = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30,
        )
    except requests.RequestException as e:
        raise RuntimeError(f"火山引擎 TTS 网络请求失败: {e}")

    if resp.status_code != 200:
        raise RuntimeError(
            f"火山引擎 TTS HTTP 错误 {resp.status_code}: {resp.text[:500]}"
        )

    # Agent Plan v3 模式：直接返回二进制音频数据
    content_type = resp.headers.get("Content-Type", "")
    if is_plan and ("audio" in content_type or len(resp.content) > 1000):
        logger.info(f"[Volcano TTS] Agent Plan 合成成功: {len(resp.content)} bytes, reqid={request_id}")
        return resp.content

    # 解析 JSON 响应（v1 模式或 v3 异常情况）
    try:
        result = resp.json()
    except json.JSONDecodeError:
        # 某些情况下直接返回音频二进制
        if len(resp.content) > 1000:
            return resp.content
        raise RuntimeError(f"火山引擎 TTS 返回格式异常: {resp.text[:500]}")

    # 检查返回码
    code = result.get("code", -1)
    if code != 3000:
        msg = result.get("message", "未知错误")
        raise RuntimeError(f"火山引擎 TTS 合成失败 (code={code}): {msg}")

    # 提取 base64 编码的音频数据
    import base64
    audio_b64 = result.get("data", "")
    if not audio_b64:
        raise RuntimeError("火山引擎 TTS 返回数据为空")

    audio_bytes = base64.b64decode(audio_b64)
    logger.info(f"[Volcano TTS] 合成成功: {len(audio_bytes)} bytes, reqid={request_id}")
    return audio_bytes


def synthesize_to_file(text: str, output_path: Path, config: VolcanoConfig) -> Path:
    """
    合成文本并保存到文件。

    Args:
        text:        要合成的文本
        output_path: 输出文件路径
        config:      火山引擎配置

    Returns:
        保存的文件路径
    """
    audio_bytes = synthesize_text(text, config)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(audio_bytes)
    logger.info(f"[Volcano TTS] 音频已保存: {output_path}")
    return output_path


def audition_voices(
    text: str,
    config: VolcanoConfig,
    output_dir: Path,
    voices: dict[str, str] | None = None,
) -> list[Path]:
    """
    用同一段文字生成多个音色的试听片段。

    Args:
        text:       试听文本
        config:     基础配置（voice_type 会被逐个覆盖）
        output_dir: 试听片段输出目录
        voices:     {显示名: voice_type_id}，默认使用 RECOMMENDED_VOICES

    Returns:
        生成的试听文件路径列表
    """
    if voices is None:
        voices = RECOMMENDED_VOICES

    output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for name, voice_id in voices.items():
        try:
            cfg = VolcanoConfig(
                app_id=config.app_id,
                api_key=config.api_key,
                cluster_id=config.cluster_id,
                voice_type=voice_id,
                speed_ratio=config.speed_ratio,
                encoding=config.encoding,
            )
            out_file = output_dir / f"audition_{name}.{config.encoding}"
            synthesize_to_file(text, out_file, cfg)
            results.append(out_file)
            print(f"  ✅ {name} ({voice_id}) → {out_file.name}")
        except Exception as e:
            print(f"  ❌ {name} ({voice_id}) 失败: {e}")

    return results
