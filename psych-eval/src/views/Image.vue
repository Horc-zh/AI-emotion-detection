<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-100 to-blue-300 p-6">
    <div class="bg-white/90 backdrop-blur-md p-10 rounded-3xl shadow-2xl w-full max-w-3xl border border-gray-200">
      <h2 class="text-4xl font-bold text-gray-800 mb-8 text-center">🖌️ 图片心理评估</h2>

      <!-- 文件上传区域 -->
      <div class="mb-6 text-center">
        <!-- 隐藏的文件输入框 -->
        <input
          id="fileInput"
          type="file"
          accept="image/*"
          @change="onFileChange"
          class="hidden"
        />

        <!-- 自定义样式的按钮 -->
        <label
          for="fileInput"
          class="inline-block bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-6 rounded-lg shadow-md cursor-pointer transition duration-300"
        >
          📁 选择图片
        </label>

        <!-- 显示已选择的文件名 -->
        <div v-if="selectedFileName" class="mt-2 text-gray-600">
          已选文件：{{ selectedFileName }}
        </div>
      </div>

      <!-- 画布区域 -->
      <div class="flex flex-col items-center">
        <canvas
          ref="canvas"
          width="400"
          height="400"
          class="border border-gray-300 rounded-lg shadow-md mb-4"
          @mousedown="startDrawing"
          @mousemove="draw"
          @mouseup="stopDrawing"
          @mouseleave="stopDrawing"
        ></canvas>

        <!-- 清除按钮 -->
        <button
          @click="clearCanvas"
          class="bg-red-500 hover:bg-red-600 text-white py-2 px-6 rounded-lg shadow-md transition duration-300 mb-6"
        >
          🗑️ 清除画布
        </button>
      </div>

      <!-- 画笔颜色选择器 -->
      <div class="flex justify-center gap-4 mb-6">
        <button
          v-for="color in colors"
          :key="color"
          :style="{ backgroundColor: color }"
          @click="setColor(color)"
          :class="[
            'w-10 h-10 rounded-full border-2',
            currentColor === color ? 'ring-4 ring-offset-2 ring-gray-500' : 'border-white',
            'hover:ring-2 hover:ring-offset-2 hover:ring-gray-400'
          ]"
        ></button>
      </div>

      <!-- 上传按钮 -->
      <div class="text-center">
        <button
          @click="uploadImage"
          :disabled="loading || (!drawingDone && !selectedFile)"
          class="w-full bg-green-500 hover:bg-green-600 text-white py-3 px-6 rounded-xl transition duration-300 disabled:opacity-50"
        >
          {{ loading ? '上传中…' : '上传并评估' }}
        </button>
      </div>

      <!-- 评估结果展示 -->
      <div v-if="evaluationResult" class="mt-8 bg-white p-6 rounded-xl shadow-inner text-left" id="result">
        <h3 class="text-xl font-semibold mb-2">评估结果</h3>
        <p class="mb-1">
          情绪倾向：<span class="font-medium">{{ evaluationResult.emotion }}</span>
        </p>
        <p class="mb-4">
          简要分析：<span class="font-medium">{{ evaluationResult.analysis }}</span>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ImageUploader',
  data() {
    return {
      // 画布绘制
      drawing: false,
      drawingDone: false,
      ctx: null,
      currentColor: '#000000',
      colors: ['#000000', '#FF5733', '#33FF57', '#3357FF', '#F1C40F'],
      // 文件上传
      selectedFile: null,
      selectedFileName: '',
      // 评估结果与状态
      evaluationResult: null,
      loading: false,
    };
  },
  methods: {
    // 画笔事件
    startDrawing(event) {
      this.drawing = true;
      const canvas = this.$refs.canvas;
      this.ctx = canvas.getContext('2d');
      this.ctx.beginPath();
      this.ctx.moveTo(event.offsetX, event.offsetY);
    },
    draw(event) {
      if (!this.drawing) return;
      this.ctx.lineTo(event.offsetX, event.offsetY);
      this.ctx.strokeStyle = this.currentColor;
      this.ctx.lineWidth = 5;
      this.ctx.lineCap = 'round';
      this.ctx.stroke();
    },
    stopDrawing() {
      if (this.drawing) {
        this.drawing = false;
        this.drawingDone = true;
      }
    },
    clearCanvas() {
      const canvas = this.$refs.canvas;
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      this.drawingDone = false;
    },
    setColor(color) {
      this.currentColor = color;
    },
    // 文件选择
    onFileChange(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedFile = file;
        this.selectedFileName = file.name;
        // 清除画布状态
        this.clearCanvas();
      }
    },
    // 上传逻辑
    uploadImage() {
      if (!this.drawingDone && !this.selectedFile) return;

      this.loading = true;

      // 模拟评估结果
      this.evaluationResult = {
        emotion: '平静',
        analysis: '从图像的颜色和形状分析，用户心情为平静',
      };

      // 滚动到结果区域
      this.$nextTick(() => {
        document.getElementById('result')?.scrollIntoView({ behavior: 'smooth' });
      });

      this.loading = false;
    },
  },
};
</script>

<style scoped>
/* 可根据需要添加自定义样式 */
</style>
