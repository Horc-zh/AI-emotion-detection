# app/services/image_logic.py

import os
import io
import base64
import json
import re
import requests
import logging
from openai import OpenAI, OpenAIError
from PIL import Image

# ---------- 配置项 ----------
DEEPSEEK_API_KEY    = os.getenv("DEEPSEEK_API_KEY", "sk-e1927ee1ea204a22b49fa3667f70a033")
DEEPSEEK_BASE_URL   = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
USE_LOCAL_INFERENCE = False  # True 使用本地推理服务，False 使用 DeepSeek API
INFERENCE_URL       = os.getenv("INFERENCE_URL", "http://localhost:11434")
INFERENCE_MODEL     = os.getenv("INFERENCE_MODEL", "deepseek-r1:1.5b")

# 日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 初始化 DeepSeek 客户端
api_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)


def analyze_image(image_path: str) -> dict:
    """
    对图片进行心理评估。优先使用本地推理，否则调用 DeepSeek API。
    返回 JSON 对象，仅包括：
      - emotion: string
      - analysis: string
    """
    # 1. 打开并压缩图像
    with Image.open(image_path) as img:
        max_dimensions = (512, 512)
        img.thumbnail(max_dimensions, Image.LANCZOS)

        # 将图像保存到内存中
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        raw = buffered.getvalue()

    # 2. Base64 编码
    b64 = base64.b64encode(raw).decode("utf-8")

    # 3. 构造提示词，指定 emotion 和 analysis，并加入严格 JSON 指令
    system_prompt = (
        "你是一位资深心理学家助手。\n"
        "请严格只返回一个 JSON 对象，且仅包含 emotion 和 analysis 两个字段，\n"
        "不要包含任何多余文字或标记，并使用中文回答。"
    )
    user_prompt = (
        "以下为 JSON 模板，请严格参照此结构返回：\n"
        "{\n"
        "  \"emotion\": \"string\",  // 主要情绪，如 高兴, 伤心, 平静 等\n"
        "  \"analysis\": \"string\"  // 简洁分析说明\n"
        "}\n"
        "现在对以下 Base64 图片数据进行分析，并仅以纯 JSON 格式输出上述格式，\n"
        "请严格使用中文回答，不要多余说明。"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt},
        {"role": "user",   "content": f"data:image/png;base64,{b64}"}
    ]

    # 4. 调用推理
    if USE_LOCAL_INFERENCE:
        raw_resp = _invoke_local(messages)
    else:
        raw_resp = _invoke_deepseek(messages)

    # 5. 提取并解析 JSON
    return _safe_parse_json(raw_resp)


def _invoke_deepseek(messages: list) -> str:
    """调用 DeepSeek 云 API 并返回原始文本或 JSON"""
    try:
        resp = api_client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
    except OpenAIError as e:
        logger.error("DeepSeek API 调用失败: %s", e)
        raise RuntimeError(f"DeepSeek API 调用失败: {e}")

    # 调试输出完整响应
    logger.debug("DeepSeek full response: %r", resp)

    choice = resp.choices[0]
    msg = getattr(choice, 'message', choice)

    # 优先使用结构化 JSON 字段
    json_data = None
    if hasattr(msg, 'json') and isinstance(msg.json, (dict, list)):
        json_data = msg.json
    elif isinstance(msg, dict) and 'json' in msg:
        json_data = msg['json']

    if json_data is not None:
        return json.dumps(json_data)

    # 回退到 content
    content = (getattr(msg, 'content', None) or '').strip()
    if not content:
        logger.warning("DeepSeek 返回空内容，消息: %r", choice)
        raise RuntimeError("DeepSeek 返回空内容，请检查提示或模型状态。")
    return content


def _invoke_local(messages: list) -> str:
    """调用本地推理服务 (Ollama HTTP API) 并返回原始文本或 JSON"""
    url = f"{INFERENCE_URL.rstrip('/')}/v1/chat/completions"
    payload = {
        "model": INFERENCE_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500,
        "stream": False,
        "response_format": {"type": "json_object"}
    }
    r = requests.post(url, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()

    logger.debug("本地推理完整响应: %s", data)

    # 本地推理返回格式处理
    if "choices" in data and data["choices"]:
        msg = data["choices"][0].get("message", {})
        if isinstance(msg, dict) and 'json' in msg:
            return json.dumps(msg['json'])
        return (msg.get('content') or '').strip()

    fallback = data.get("message", {}).get("content", "").strip()
    if not fallback:
        logger.warning("本地推理返回空内容: %s", data)
        raise RuntimeError("本地推理返回空内容，请检查服务状态。")
    return fallback


def _extract_json_block(text: str) -> str:
    """
    从文本中提取 JSON 区块：
    1. 匹配 ```json ... ```
    2. 否则提取第一个 { ... }
    """
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.S)
    if m:
        return m.group(1)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
    return text


def _safe_parse_json(text: str) -> dict:
    """
    尝试解析 JSON；解析失败则以原文为 analysis，
    emotion 默认为 None。
    """
    clean = _extract_json_block(text).strip()
    try:
        data = json.loads(clean)
        return {"emotion": data.get("emotion"), "analysis": data.get("analysis")}  
    except json.JSONDecodeError:
        logger.error("JSON 解析失败: %s", clean)
        return {"emotion": None, "analysis": text.strip()}
