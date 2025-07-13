import os
import base64
import json
from flask import Blueprint, request, jsonify
from app.services.evaluate_logic import evaluate_all, analyze_image

evaluate_bp = Blueprint('evaluate', __name__, url_prefix='/api/evaluate')

@evaluate_bp.route('', methods=['POST'], strict_slashes=False)
def evaluate():
    """
    接收前端 JSON：
      - ageGroup: 年龄组
      - gender: 性别
      - text: 文本描述
      - questions: 问卷结构列表
      - responses: 用户回答列表
      - drawing: Base64 数据 URL 或纯 Base64 字符串
    然后调用 evaluate_all 返回评估结果。
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "无效的 JSON 请求"}), 400

        # 基本字段
        age_group = data.get('ageGroup', None)
        gender    = data.get('gender', None)
        text_input    = data.get('text', '')
        questions_data = data.get('questions', [])
        survey_answers = data.get('responses', [])

        # 处理 Base64 绘图（可接受 data URL 或纯 base64）
        drawing_data = data.get('drawing')
        image_analysis = None
        if drawing_data:
            # 如果是 data URL 格式，去除前缀
            if drawing_data.startswith('data:'):
                _, b64 = drawing_data.split(',', 1)
            else:
                b64 = drawing_data
            img_bytes = base64.b64decode(b64)

            # 临时保存文件以供 analyze_image 使用
            save_dir = os.getenv('TEMP_IMAGE_DIR', '/tmp')
            os.makedirs(save_dir, exist_ok=True)
            tmp_path = os.path.join(save_dir, 'drawing.png')
            with open(tmp_path, 'wb') as f:
                f.write(img_bytes)

            img_result = analyze_image(tmp_path)
            if isinstance(img_result, dict):
                image_analysis = json.dumps(img_result, ensure_ascii=False)
            else:
                image_analysis = str(img_result)

            try:
                os.remove(tmp_path)
            except OSError:
                pass

        # 调用综合评估逻辑
        result_text = evaluate_all(
            text_input,
            survey_answers,
            image_analysis,
            questions_data,
            age_group,
            gender
        )

        return jsonify({"result": result_text}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
