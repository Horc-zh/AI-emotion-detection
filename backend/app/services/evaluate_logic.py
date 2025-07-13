import os
import json
import base64
import re
import requests
from openai import OpenAI, OpenAIError
from app.services.questions_data import QUESTIONS

# DeepSeek 云 API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-e1927ee1ea204a22b49fa3667f70a033")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# 本地推理服务配置（Ollama / LocalAI OpenAI-兼容接口）
USE_LOCAL_INFERENCE = False  # True 使用本地推理服务，False 使用 DeepSeek API
INFERENCE_URL       = os.getenv("INFERENCE_URL", "http://localhost:11434/v1/chat/completions")
INFERENCE_MODEL     = os.getenv("INFERENCE_MODEL", "deepseek-r1:1.5b")

# 初始化 DeepSeek 客户端（云端）
api_client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL
)


def remove_think_tags(text):
    """移除 <think> 标签及其内容"""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)


def evaluate_all(text_input: str,
                 questions: list,
                 survey_answers: list,
                 image_analysis: str = None,
                 age_group: str = None,
                 gender: str = None) -> str:
    """
    综合评估入口：接收文本描述、题目列表、问卷答案、可选的图像分析结果，以及年龄组和性别。
    然后根据 USE_LOCAL_INFERENCE 选择本地或云端推理返回评估文本。
    """
    parts = [
        f"年龄组：{age_group or 'unknown'}",
        f"性别：{gender or 'unknown'}",
        f"用户文本描述：\n{text_input}",
        f"问卷题目：\n{json.dumps(questions, ensure_ascii=False, indent=2)}",
        f"用户回答：\n{json.dumps(survey_answers, ensure_ascii=False)}"
    ]
    if image_analysis:
        parts.append(f"图像分析结果：\n{image_analysis}")

    # 添加明确的报告结构提示词
    parts.append(
        "请作为心理健康专家，基于以上信息撰写一份专业的心理健康评估报告，"
        "报告应包括以下部分：\n"
        "1. 综合心理评价\n"
        "2. 当前情绪状态\n"
        "3. 工作与生活中的压力源分析\n"
        "4. 人际关系状况评估\n"
        "5. 建议与应对策略\n"
        "请使用专业且易于理解的语言，避免使用非正式或模糊的词汇。"
    )
    prompt = "\n\n".join(parts)

    # 本地推理
    if USE_LOCAL_INFERENCE:
        payload = {
            "model": INFERENCE_MODEL,
            "messages": [
                {"role": "system", "content": "你是一位资深心理健康评估专家。"},
                {"role": "user",   "content": prompt}
            ],
            "stream": False
        }
        resp = requests.post(INFERENCE_URL, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return remove_think_tags(data["choices"][0]["message"]["content"].strip())

    # 云端 DeepSeek
    try:
        resp = api_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一位资深心理健康评估专家。"},
                {"role": "user",   "content": prompt}
            ],
            stream=False
        )
        return remove_think_tags(resp.choices[0].message.content.strip())
    except OpenAIError as e:
        raise RuntimeError(f"DeepSeek 云调用失败: {e}")



def analyze_image(image_path: str) -> dict:
    """
    对上传的本地图片文件进行分析，返回一个 dict 结构：
    先将图片 Base64 编码，然后传给模型，最终解析模型输出为 JSON 或 raw 文本。
    """
    try:
        with open(image_path, "rb") as f:
            raw = f.read()
        b64 = base64.b64encode(raw).decode("utf-8")
    except Exception as e:
        raise RuntimeError(f"无法读取或编码图片: {e}")

    messages = [
        {
            "role": "system",
            "content": (
                "你是一名资深心理学家助手，"
                "善于从用户上传的图片中捕捉情感变化、色彩氛围等心理线索，"
                "并给出简洁有力的心理评估。"
            )
        },
        {
            "role": "user",
            "content": (
                f"<ImageData>data:image/jpeg;base64,{b64}</ImageData>\n\n"
                "请你基于这张图片的内容给出心理评估，"
                "包括主要情绪倾向和置信度（0-1）。"
            )
        }
    ]

    if USE_LOCAL_INFERENCE:
        return _analyze_image_local(messages)
    else:
        return _analyze_image_deepseek_api(messages)


# ... 其余 _analyze_image_deepseek_api、_analyze_image_local 和 _parse_response 保持不变 ...


def _analyze_image_deepseek_api(messages: list) -> dict:
    """调用 DeepSeek 云 API 进行图片分析"""
    try:
        resp = api_client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
    except OpenAIError as e:
        raise RuntimeError(f"DeepSeek API 请求失败: {e}")

    content = resp.choices[0].message.content.strip()
    return _parse_response(content)


def _analyze_image_local(messages: list) -> dict:
    """调用本地推理服务进行图片分析"""
    try:
        r = requests.post(INFERENCE_URL, json={
            "model": INFERENCE_MODEL,
            "messages": messages,
            "stream": False
        }, timeout=60)
        r.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"本地推理请求失败: {e}")

    data = r.json()
    # 兼容多种字段命名
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    if not content:
        raise RuntimeError("本地推理未返回内容")

    # 去除 <think> 标签
    cleaned = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
    return _parse_response(cleaned)


def _parse_response(text: str) -> dict:
    """
    尝试解析模型返回的 JSON 格式；失败时返回 {'raw': text}。
    """
    try:
        return json.loads(text)
    except ValueError:
        return {"raw": text}
