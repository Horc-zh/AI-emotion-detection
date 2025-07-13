# app/routes/survey.py
from flask import Blueprint, request, jsonify, session
from app.services.survey_logic import process_survey

survey_bp = Blueprint('survey', __name__)

@survey_bp.route('', methods=['POST'], strict_slashes=False)
def submit_survey():
    """提交问卷回答并返回评分和建议"""
    data = request.get_json() or {}

    print("DEBUG payload:", data)
    questions = data.get('questions')
    responses = data.get('responses')
    age_group = data.get('ageGroup')
    gender = data.get('gender')

    # 验证数据的完整性
    if not isinstance(questions, list) or not isinstance(responses, list):
        return jsonify({'error': '缺少或格式错误，需提供 questions 和 responses 列表'}), 400

    # 调用处理逻辑
    result = process_survey(questions, responses)

    # 存入 session 历史
    history = session.setdefault('survey_history', [])
    history.append({
        'questions': questions,
        'responses': responses,
        'result': result,
        'ageGroup': age_group,
        'gender': gender
    })
    session.modified = True

    # 返回完整的评估结果
    return jsonify({
        'status': 'success',
        'score': result.get('score', 0),
        'analysis': result.get('analysis', '暂无详细分析'),
        'risk_level': result.get('risk_level', 'unknown'),
        'recommendations': result.get('recommendations', [])
    })

@survey_bp.route('/history', methods=['GET'], strict_slashes=False)
def get_history():
    """返回所有提交记录，包括回答和评估结果"""
    history = session.get('survey_history', [])
    return jsonify({'history': history})

@survey_bp.route('/reset', methods=['POST'], strict_slashes=False)
def reset_survey():
    """清空问卷提交记录"""
    session['survey_history'] = []
    session.modified = True
    return jsonify({'status': 'survey history reset'})
