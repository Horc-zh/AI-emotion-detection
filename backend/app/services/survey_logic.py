# app/services/survey_logic.py

import os
import re
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List
from openai import OpenAI

# ---------- 日志配置（全局开启 DEBUG 级别） ----------
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

# ---------- 配置项（建议通过环境变量管理） ----------
DEEPSEEK_API_KEY    = os.getenv("DEEPSEEK_API_KEY", "sk-e1927ee1ea204a22b49fa3667f70a033")
DEEPSEEK_BASE_URL   = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
USE_LOCAL_INFERENCE = False  # True 使用本地推理服务，False 使用 DeepSeek API
INFERENCE_URL       = os.getenv("INFERENCE_URL", "http://localhost:11434")
INFERENCE_MODEL     = os.getenv("INFERENCE_MODEL", "deepseek-r1:1.5b")

api_client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL
)

def process_survey(questions: List[str], responses: List[int]) -> Dict:
    """
    根据前端传入的 questions 和 responses 生成评估结果。
    questions: 每一道题的文本列表
    responses: 与 questions 等长的回答列表（0-3）
    """
    try:
        validate_responses(questions, responses)
        prompt = build_assessment_prompt(questions, responses)

        if USE_LOCAL_INFERENCE:
            raw = analyze_with_inference_server(prompt)
        else:
            raw = get_deepseek_response(prompt)

        result = standardize_response(raw)
        logging.debug(f"Standardized response: {result}")
        return result

    except Exception as e:
        logging.error(f"process_survey 全面失败：{e}", exc_info=True)
        return error_response()


def validate_responses(questions: List[str], responses: List[int]):
    """
    确保题目与回答一一对应，且每个回答在合法范围内。
    """
    if len(responses) != len(questions):
        raise ValueError(f"题目数 ({len(questions)}) 与回答数 ({len(responses)}) 不匹配")
    if any(not isinstance(r, int) or r < 0 or r > 3 for r in responses):
        raise ValueError("无效的回答值，必须为 0-3 的整数")


def build_assessment_prompt(questions: List[str], responses: List[int]) -> str:
    """
    拼接成 LLM 可用的「JSON 返回格式」提示词。
    在此处添加提示词工程：
    1. 明确要求在低风险场景下也要给出“低风险”反馈
    2. 仅在确实信息严重不足时，才返回“信息不足”提示
    """
    details = "\n".join(
        f"{i+1}. {questions[i]} → 回答：{responses[i]}分"
        for i in range(len(questions))
    )
    enhanced_instructions = (
        "请严格按照以下要求返回 JSON：\n"
        "- score: 0-100 数值，代表风险指数\n"
        "- risk_level: 'low'/'medium'/'high'，仅使用这三个英文标签\n"
        "- analysis: 简洁文字分析。若大部分回答为最低风险，必须返回“低风险”说明；\n"
        "  仅在回答逻辑无法评估时，返回“信息不足”提示。\n"
        "- recommendations: 针对 risk_level 提供 2-3 条专业建议\n"
    )
    return f"{enhanced_instructions}\n用户回答详情：\n{details}"  


def get_deepseek_response(prompt: str, retries: int = 3) -> Dict:
    for attempt in range(1, retries + 1):
        try:
            resp = api_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一位专业心理医生，输出严格 JSON 格式，不要额外说明。"},
                    {"role": "user",   "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            raw = resp.choices[0].message.content
            # 清理 ```json 包裹
            if raw.startswith("```json"):
                raw = raw.split("```json",1)[1].rsplit("```",1)[0].strip()
            return json.loads(raw)
        except Exception as e:
            logging.warning(f"[DeepSeek API 尝试 {attempt}] 失败: {e}")
    raise Exception("DeepSeek API 请求失败")


def analyze_with_inference_server(prompt: str) -> Dict:
    url = f"{INFERENCE_URL.rstrip('/')}/v1/chat/completions"
    payload = {
        "model": INFERENCE_MODEL,
        "messages": [
            {"role": "system", "content": "你是一位专业心理医生，输出严格 JSON，仅返回结果，不要多余文本。"},
            {"role": "user",   "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 500
    }
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    # 提取首个 ```json … ``` 区块
    m = re.search(r"```json\s*(\{.*?\})\s*```", content, re.S)
    if not m:
        raise ValueError("无法提取 JSON 区块")
    return json.loads(m.group(1))


def standardize_response(raw: Dict) -> Dict:
    fields = ["score", "analysis", "risk_level", "recommendations"]
    if not all(f in raw for f in fields):
        raise ValueError("响应字段不完整")
    score = max(0, min(int(raw["score"]), 100))
    risk  = raw["risk_level"].lower()
    recs  = raw["recommendations"] if isinstance(raw["recommendations"], list) else [str(raw["recommendations"])]
    return {"score": score, "analysis": raw["analysis"], "risk_level": risk, "recommendations": recs}


def error_response() -> Dict:
    return {"score": None, "analysis": "评估服务不可用", "risk_level": "unknown", "recommendations": ["请稍后重试"]}
