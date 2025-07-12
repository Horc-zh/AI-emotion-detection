<template>
  <div class="evaluate-container">
    <h1 class="text-4xl font-bold mb-8 text-center">🧠 心理综合评估</h1>

    <!-- 📝 心情描述 -->
    <div class="section">
      <h2 class="text-2xl font-bold mb-4">📝 请描述您的当前心情</h2>
      <textarea
        v-model="textInput"
        placeholder="请输入您的感受..."
        rows="6"
        style="width: 100%; height: 150px;"
        class="bg-gradient-to-br from-green-100 to-green-300 p-6"
      ></textarea>
    </div>

    <!-- 📋 问卷部分 -->
    <div class="section">
      <h2 class="text-2xl font-bold mb-4">📋 {{ genderLabel }} {{ ageGroupLabel }} 问卷</h2>
      <div
        v-for="(question, index) in questions"
        :key="index"
        class="question-block"
      >
        <p>{{ index + 1 }}. {{ question.text }}</p>
        <div class="options">
          <label v-for="(option, idx) in question.options" :key="idx">
            <input
              type="radio"
              :name="`q${index}`"
              :value="idx"
              v-model="responses[index]"
            />
            {{ option }} &nbsp;
          </label>
        </div>
        <br/>
      </div>
    </div>

    <!-- 🎨 绘图区域 -->
    <div class="section">
      <h2 class="text-2xl font-bold mb-4">🎨 请绘制表达您感受的图像</h2>
      <div class="drawing-controls">
        <div class="color-palette">
          <button
            v-for="color in colors"
            :key="color"
            :style="{ backgroundColor: color }"
            @click="selectColor(color)"
            :class="{ active: currentColor === color }"
          ></button>
        </div>
        <button class="clear-btn" @click="clearCanvas">清除</button>
      </div>
      <canvas
        ref="canvas"
        width="600"
        height="300"
        @mousedown="startDrawing"
        @mousemove="draw"
        @mouseup="stopDrawing"
        @mouseleave="stopDrawing"
        @touchstart.prevent="startDrawingTouch"
        @touchmove.prevent="drawTouch"
        @touchend.prevent="stopDrawing"
      ></canvas>
    </div>

    <!-- 🚀 提交按钮 -->
    <div class="submit-button-container">
      <button
        class="submit-button"
        @click="submitEvaluation"
        :disabled="isSubmitting || !isFormComplete"
      >
        {{ isSubmitting ? '提交中...' : '🚀 提交评估' }}
      </button>
    </div>

    <!-- ✅ 评估结果 -->
    <div v-if="evaluationResult" class="result">
      <h2>✅ 评估结果</h2>
      <p>{{ evaluationResult }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

// —— 参数来源 —— //
const props = defineProps({
  ageGroup: { type: String, default: '' },
  gender:   { type: String, default: '' }
})
const route  = useRoute()

const ageGroupValue = computed(() => props.ageGroup || route.query.ageGroup || 'minor')
const genderValue   = computed(() => props.gender   || route.query.gender   || 'male')

// —— 本地状态 —— //
const textInput        = ref('')
const questions        = ref([])
const responses        = ref([])
const evaluationResult = ref(null)
const isSubmitting     = ref(false)

const canvas       = ref(null)
const colors       = ['#000', '#f00', '#0f0', '#00f', '#ff0', '#f0f', '#0ff']
const currentColor = ref(colors[0])
const isDrawing    = ref(false)
let lastPos        = { x: 0, y: 0 }

// —— 标签文字 —— //
const genderLabel   = computed(() => genderValue.value === 'male' ? '男性' : '女性')
const ageGroupLabel = computed(() => ageGroupValue.value === 'minor' ? '未成年' : '成年')

// —— 表单验证 —— //
const isFormComplete = computed(() => {
  const textOk   = textInput.value.trim() !== ''
  const surveyOk = responses.value.length === questions.value.length && responses.value.every(r => r !== null)
  return textOk && surveyOk
})

// —— 绘图逻辑 —— //
function getPointerPos(e) {
  const rect = canvas.value.getBoundingClientRect()
  return {
    x: ((e.clientX - rect.left) * canvas.value.width) / rect.width,
    y: ((e.clientY - rect.top)  * canvas.value.height) / rect.height
  }
}
function selectColor(color) {
  currentColor.value = color
}
function clearCanvas() {
  const ctx = canvas.value.getContext('2d')
  ctx.clearRect(0, 0, canvas.value.width, canvas.value.height)
}
function startDrawing(e) {
  isDrawing.value = true
  lastPos = getPointerPos(e)
}
function draw(e) {
  if (!isDrawing.value) return
  const pos = getPointerPos(e)
  const ctx = canvas.value.getContext('2d')
  ctx.strokeStyle = currentColor.value
  ctx.lineWidth   = 2
  ctx.lineCap     = 'round'
  ctx.beginPath()
  ctx.moveTo(lastPos.x, lastPos.y)
  ctx.lineTo(pos.x, pos.y)
  ctx.stroke()
  lastPos = pos
}
function stopDrawing() {
  isDrawing.value = false
}
function startDrawingTouch(e) {
  startDrawing(e.touches[0])
}
function drawTouch(e) {
  draw(e.touches[0])
}

// —— 问卷加载 —— //
onMounted(async () => {
  try {
    const module = await import(
      /* @vite-ignore */ `../data/survey-${ageGroupValue.value}-${genderValue.value}.json`
    )
    questions.value = module.default
    responses.value = Array(questions.value.length).fill(null)
  } catch (err) {
    console.error('加载问卷失败', err)
    alert('未能加载问卷，请检查配置或稍后重试')
  }
})

// —— 提交评估 —— //
async function submitEvaluation() {
  if (isSubmitting.value || !isFormComplete.value) return
  isSubmitting.value = true

  try {
    const dataUrl = canvas.value.toDataURL('image/png')
    const payload = {
      ageGroup : ageGroupValue.value,
      gender   : genderValue.value,
      text     : textInput.value,
      questions: questions.value,
      responses: responses.value,
      drawing  : dataUrl
    }

    const { data } = await axios.post('/api/evaluate', payload)
    evaluationResult.value = data.result
  } catch (err) {
    console.error('评估失败:', err)
    evaluationResult.value = '评估失败，请稍后再试。'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.evaluate-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
.section {
  margin-bottom: 2rem;
}
.drawing-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}
.color-palette {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
}
.color-palette button {
  width: 24px;
  height: 24px;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
}
.color-palette button.active {
  outline: 2px solid #555;
}
.clear-btn {
  background-color: #e74c3c;
  color: #fff;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
}
canvas {
  border: 1px solid #ccc;
  border-radius: 4px;
  touch-action: none;
}
button[disabled] {
  opacity: 0.6;
  cursor: not-allowed;
}
.result {
  margin-top: 2rem;
  padding: 1rem;
  background-color: #f0f0f0;
  border-radius: 8px;
}
.submit-button-container {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}
.submit-button {
  font-size: 1.25rem;
  padding: 1rem 2rem;
  background-color: #3498db;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
.submit-button:hover {
  background-color: #2980b9;
}
</style>
