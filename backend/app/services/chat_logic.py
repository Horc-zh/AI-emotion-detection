# app/services/chat_logic.py

import re
import requests
from datetime import datetime
from openai import OpenAI

# 模式切换：True 使用本地 Ollama，False 使用 DeepSeek API
USE_OLLAMA = False

# 本地模型配置
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "deepseek-r1:1.5b"  # 本地模型名称

# DeepSeek API 客户端配置
client = OpenAI(
    api_key="sk-e1927ee1ea204a22b49fa3667f70a033",
    base_url="https://api.deepseek.com"
)

MAX_HISTORY = 8  # 保留最近8轮对话

def process_chat(full_history, instruction=None):
    try:
        optimized_history = optimize_context(full_history.copy())

        # 如果提供了额外的系统指令，插入到历史记录的最前面
        if instruction:
            optimized_history.insert(0, {"role": "system", "content": instruction})

        if USE_OLLAMA:
            return chat_with_ollama(optimized_history)
        else:
            return chat_with_api(optimized_history)

    except Exception as e:
        log_error(e)
        return "当前服务繁忙，请稍后再试"

def chat_with_api(messages):
    """调用 DeepSeek 官方 API 聊天"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message.content

def chat_with_ollama(messages):
    # 拼接 prompt
    prompt = ""
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "system":
            prompt += f"System: {content}\n"
        elif role == "user":
            prompt += f"User: {content}\n"
        elif role == "assistant":
            prompt += f"Assistant: {content}\n"
    prompt += "Assistant:"

    try:
        print("🔧 正在向 Ollama 发送请求...")
        print("📤 Prompt:")
        print(prompt)

        res = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        print(f"📥 状态码: {res.status_code}")
        print(f"📥 响应: {res.text}")

        if res.status_code == 200:
            response = res.json().get("response", "").strip()
            if response:
                # 在终端打印完整响应
                print("完整响应:")
                print(response)

                # 使用正则表达式移除 <think> 标签及其内容
                cleaned_response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()
                return cleaned_response
            else:
                log_error("Ollama returned empty response.")
                return "未能获得有效的模型回复"
        else:
            log_error(f"Ollama error: {res.status_code} - {res.text}")
            return "本地模型服务暂不可用"

    except requests.exceptions.RequestException as e:
        log_error(f"Ollama request error: {e}")
        return "本地模型服务暂不可用"

def optimize_context(history):
    """优化上下文长度策略"""
    if len(history) > MAX_HISTORY + 1:
        return [history[0]] + history[-MAX_HISTORY:]
    return history

def log_error(error):
    """错误日志记录"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open("chat_errors.log", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {str(error)}\n")
    except Exception as file_error:
        print(f"日志写入失败：{file_error}")
