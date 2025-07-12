<template>
  <div class="report-container">
    <h1>心理评估报告</h1>
    <pre class="report-content">{{ report }}</pre>
    <button @click="goBack" class="btn back-btn">返回对话</button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const props = defineProps({
  report: String
})

const router = useRouter()
const goBack = () => {
  router.push('/chat')  // 返回聊天页
}
</script>

<style scoped>
.report-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 24px;
  background: #fefefe;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.report-content {
  white-space: pre-wrap;
  background-color: #f0f4c3;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #cddc39;
  color: #333;
  line-height: 1.6;
}
.back-btn {
  margin-top: 20px;
  background: #1976d2;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.back-btn:hover {
  filter: brightness(0.9);
}
</style>
