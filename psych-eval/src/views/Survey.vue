<template>
  <div class="survey-container">
    <h2>📝 {{ genderLabel }} {{ ageGroupLabel }} 问卷</h2>
    <form @submit.prevent="submitSurvey">
      <div
        v-for="(question, index) in questions"
        :key="index"
        class="question-block"
      >
        <p>{{ index + 1 }}. {{ question.text }}</p>
        <div class="options">
          <label
            v-for="(option, idx) in question.options"
            :key="idx"
            class="option-label"
          >
            <input
              type="radio"
              :name="`q${index}`"
              :value="idx"
              v-model="responses[index]"
              required
              :disabled="isSubmitting"
            />
            {{ option }}
          </label>
        </div>
      </div>

      <!-- 提交按钮容器 -->
      <div class="submit-button-container">
        <button type="submit" :disabled="isSubmitting || !isFormComplete" class="submit-button">
          <span v-if="isSubmitting" class="loader"></span>
          {{ submitButtonText }}
        </button>
      </div>
    </form>

    <!-- 评估结果模态框 -->
    <div v-if="showResult" class="result-modal" @click.self="closeModal">
      <div class="modal-content">
        <h3>📋 心理健康评估报告</h3>
        <div class="risk-level" :class="result.risk_level">
          {{ chineseRiskLevel[result.risk_level] }}
        </div>
        <div class="score-section">
          <div class="score-box">
            <div class="score-value">{{ result.score }}</div>
            <div class="score-label">标准化评分</div>
          </div>
          <div class="score-range">（评估范围 0-100 分）</div>
        </div>
        <div class="analysis-section">
          <h4>🔍 详细分析</h4>
          <p>{{ result.analysis }}</p>
        </div>
        <div class="recommendations-section">
          <h4>💡 专业建议</h4>
          <ul>
            <li v-for="(item, idx) in result.recommendations" :key="idx">
              {{ item }}
            </li>
          </ul>
        </div>
        <!-- 复用提交按钮样式，额外加 cancel-button 类 -->
        <button class="submit-button cancel-button" @click="closeModal">
          关闭报告
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>

import { ref, computed, onMounted, toRaw } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const { age, gender } = route.query

// 计算年龄组
const ageGroup = computed(() => (age < 18 ? 'minor' : 'adult'))

// 动态加载问卷
const questions = ref([])
const responses = ref([])

const isSubmitting = ref(false)
const showResult = ref(false)
const result = ref({
  score: 0,
  analysis: '',
  risk_level: 'unknown',
  recommendations: []
})

// 标签计算
const genderLabel = computed(() => (gender === 'male' ? '男性' : '女性'))
const ageGroupLabel = computed(() =>
  ageGroup.value === 'minor' ? '未成年' : '成年'
)

// 表单完成检查
const isFormComplete = computed(
  () =>
    responses.value.length > 0 && responses.value.every((r) => r !== null)
)
const submitButtonText = computed(
  () =>
    isSubmitting.value
      ? '评估中...'
      : isFormComplete.value
      ? '提交评估'
      : '请完成所有题目'
)

const chineseRiskLevel = {
  low: '低风险：心理健康状态良好',
  medium: '中风险：需要关注心理状态',
  high: '高风险：建议寻求专业帮助',
  unknown: '评估结果不可用'
}

// 加载对应问卷
onMounted(async () => {
  try {
    const file = `/src/data/survey-${ageGroup.value}-${gender}.json`
    const module = await import(/* @vite-ignore */ file)
    questions.value = module.default
    responses.value = Array(questions.value.length).fill(null)
  } catch (err) {
    console.error('加载问卷失败', err)
    alert('未能加载问卷，请检查配置或稍后重试')
    router.back()
  }
})

// 提交问卷
const submitSurvey = async () => {
  if (isSubmitting.value) return
  isSubmitting.value = true

  try {
    const payload = {
      ageGroup: ageGroup.value,
      gender,
      questions: toRaw(questions.value),
      responses: toRaw(responses.value)
    }

    const { data } = await axios.post('/api/survey', payload)

    result.value = {
      score: data.score || 0,
      analysis: data.analysis || '暂无详细分析',
      risk_level: (data.risk_level || 'unknown').toLowerCase(),
      recommendations:
        data.recommendations && data.recommendations.length
          ? data.recommendations
          : ['建议联系专业心理咨询师']
    }
    showResult.value = true
  } catch (error) {
    console.error('提交问卷失败', error)
    alert('提交失败，请稍后重试')
  } finally {
    isSubmitting.value = false
  }
}

const closeModal = () => {
  showResult.value = false
}
</script>

<style scoped>
.survey-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

/* 提交和关闭按钮的基础样式 */
.submit-button {
  font-size: 1.25rem;
  padding: 1rem 2rem;
  border-radius: 8px;
  color: white;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.submit-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

/* 提交按钮绿色 */
.submit-button:not(.cancel-button) {
  background-color: #4CAF50;
}
.submit-button:not(.cancel-button):hover {
  background-color: #45a049;
}

/* 取消/关闭按钮红色 */
.cancel-button {
  background-color: #E53935;
}
.cancel-button:hover {
  background-color: #D32F2F;
}

/* 提交按钮容器 */
.submit-button-container {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

/* 结果模态框样式 */
.result-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: #fff;
  padding: 2rem;
  border-radius: 12px;
  max-width: 600px;
  width: 90%;
}

.risk-level.low {
  color: #4caf50;
}
.risk-level.medium {
  color: #ff9800;
}
.risk-level.high {
  color: #f44336;
}

/* 其他样式保持不变... */
</style>
