from flask import Blueprint, request, jsonify, session
from app.services.chat_logic import process_chat

chat_bp = Blueprint('chat', __name__)

SYSTEM_PROMPT = {
    "role": "system",
    "content": """你是一位专业心理咨询师，请遵循以下原则：
1. 保持共情和耐心
2. 逐步引导用户深入表达
3. 注意识别心理风险信号
4. 保持对话连贯性"""
}

@chat_bp.route('/', methods=['POST'])
def handle_chat():
    """主聊天端点"""
    if 'chat_history' not in session:
        session['chat_history'] = [SYSTEM_PROMPT]

    data = request.get_json() or {}
    history = data.get('messages')
    if isinstance(history, list):
        session['chat_history'] = history
        user_message = history[-1].get('content', '')
    else:
        user_message = data.get('message')
        if not user_message:
            return jsonify({'error': '缺少消息内容或格式不正确'}), 400
        session['chat_history'].append({"role": "user", "content": user_message})

    try:
        ai_reply = process_chat(session['chat_history'])
        session['chat_history'].append({"role": "assistant", "content": ai_reply})
        session.modified = True
        return jsonify({'reply': ai_reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/reset', methods=['POST'])
def handle_reset():
    """重置对话历史，仅保留系统提示"""
    session['chat_history'] = [SYSTEM_PROMPT]
    session.modified = True
    return jsonify({'status': '对话已重置'})

@chat_bp.route('/history', methods=['GET'])
def get_history():
    """返回完整的会话历史"""
    return jsonify({
        'history': session.get('chat_history', [SYSTEM_PROMPT])
    })

@chat_bp.route('/assess', methods=['POST'])
def handle_assessment():
    """心理评估端点"""
    if 'chat_history' not in session:
        return jsonify({'error': '无可用的对话历史进行评估'}), 400

    try:
        instruction = "请对以下对话内容进行心理健康分析，识别潜在的心理风险因素，并提供专业建议。"
        ai_reply = process_chat(session['chat_history'], instruction=instruction)
        return jsonify({'assessment': ai_reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
