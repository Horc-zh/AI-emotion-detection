from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os, time, base64, io
from PIL import Image
import cv2
import numpy as np
from ..services.image_logic import analyze_image

# Blueprint 注册，前缀为 /api/image
image_bp = Blueprint('image', __name__, url_prefix='/api/image')

# 上传文件存储目录 & 支持的后缀
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compress_image(image_path, max_size_kb=1):
    """
    压缩图像以确保其大小不超过指定的最大值（以KB为单位）。
    """
    img = Image.open(image_path)
    img_format = img.format
    quality = 85
    while True:
        buffer = io.BytesIO()
        img.save(buffer, format=img_format, quality=quality)
        size_kb = buffer.tell() / 1024
        if size_kb <= max_size_kb or quality <= 20:
            break
        quality -= 5
    buffer.seek(0)
    return buffer

@image_bp.route('/upload', methods=['POST'])
def upload_image():
    """
    处理图片上传：
    - 优先从 request.files['file'] 获取二进制文件
    - 否则尝试从 request.form['image'] 获取 Base64 字符串
    同时添加图像预处理：对比度增强、去噪、人脸检测与裁剪。
    """
    try:
        # 1. 文件流上传
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': '未选择文件'}), 400
            if not allowed_file(file.filename):
                return jsonify({'error': '不支持的文件类型'}), 415

            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

        # 2. Base64 字符串上传
        elif request.form.get('image'):
            b64data = request.form['image']
            # 去除可能的 data URI 前缀
            if ',' in b64data:
                b64data = b64data.split(',', 1)[1]
            raw = base64.b64decode(b64data)
            img = Image.open(io.BytesIO(raw))
            filename = f'drawing_{int(time.time())}.png'
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            img.save(filepath)

        else:
            return jsonify({'error': '未检测到上传数据'}), 400

        # --- 图像预处理流程 ---
        # 读取图像
        img_cv = cv2.imread(filepath)
        if img_cv is None:
            current_app.logger.error(f"无法读取图像文件: {filepath}")
        else:
            # 1. 转 LAB 做 CLAHE 均衡化
            lab = cv2.cvtColor(img_cv, cv2.COLOR_BGR2LAB)
            l_channel, a_channel, b_channel = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            cl = clahe.apply(l_channel)
            merged_lab = cv2.merge((cl, a_channel, b_channel))
            img_clahe = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)

            # 2. 去噪
            img_denoised = cv2.fastNlMeansDenoisingColored(
                img_clahe, None, h=10, hColor=10, templateWindowSize=7, searchWindowSize=21
            )

            # 3. 人脸检测与裁剪（可选）
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            gray = cv2.cvtColor(img_denoised, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            if len(faces) > 0:
                x, y, w, h = faces[0]
                img_processed = img_denoised[y:y+h, x:x+w]
            else:
                img_processed = img_denoised

            # 4. 调整图像尺寸
            max_dimensions = (192, 192)
            img_pil = Image.fromarray(cv2.cvtColor(img_processed, cv2.COLOR_BGR2RGB))
            img_pil.thumbnail(max_dimensions, Image.Resampling.LANCZOS)
            img_pil.save(filepath)

        # 5. 压缩图像
        compressed_buffer = compress_image(filepath, max_size_kb=100)
        compressed_image = Image.open(compressed_buffer)
        compressed_image.save(filepath)

        # 6. 调用图像分析逻辑
        result = analyze_image(filepath)
        current_app.logger.debug("分析结果 = %r", result)

        # 7. 返回评估结果
        return jsonify({'message': '上传成功', 'result': result}), 200

    except Exception as e:
        # 记录异常堆栈，便于排查
        current_app.logger.exception('上传或评估失败')
        return jsonify({'error': '服务器内部错误，请稍后重试'}), 500
