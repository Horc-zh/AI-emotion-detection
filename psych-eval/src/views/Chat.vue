<template>
  <div class="chat-container">
    <h1 class="chat-title">心理咨询对话</h1>
    <div class="chat-history">
      <div
        v-for="(msg, index) in history"
        :key="index"
        :class="['message', msg.role]"
      >
        <div class="role-tag">{{ roleMap[msg.role] }}</div>
        <div class="content">{{ msg.content }}</div>
      </div>
    </div>
    <div class="input-area">
      <textarea
        v-model="message"
        placeholder="请描述您的感受..."
        @keyup.enter="sendMessage"
      ></textarea>
      <div class="controls">
        <button @click="sendMessage" :disabled="isSending" class="btn send-btn">
          {{ isSending ? '发送中...' : '发送' }}
        </button>
        <button @click="resetChat" class="btn reset-btn">重置对话</button>
        <button @click="assessOverall" class="btn assess-btn">心理评估</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'

const message = ref('')
const isSending = ref(false)
const history = reactive([])

const roleMap = {
  system: '系统',
  user: '我',
  assistant: '咨询师'
}

// 初始化时获取历史记录（如果需要）
const initHistory = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/chat/history', {
      withCredentials: true
    })
    history.push(...res.data.history)
  } catch (error) {
    console.error('获取历史记录失败:', error)
  }
}
initHistory()

const sendMessage = async () => {
  if (!message.value.trim() || isSending.value) return

  isSending.value = true
  history.push({ role: 'user', content: message.value.trim() })
  try {
    const response = await axios.post(
      'http://localhost:5000/api/chat/',
      { messages: [...history] },
      { withCredentials: true }
    )
    history.push({ role: 'assistant', content: response.data.reply })
    message.value = ''
  } catch (error) {
    console.error('发送失败:', error)
    history.push({ role: 'system', content: '对话服务暂时不可用，请稍后再试' })
  } finally {
    isSending.value = false
  }
}

const resetChat = async () => {
  if (isSending.value) return
  isSending.value = true
  try {
    await axios.post('http://localhost:5000/api/chat/reset', {}, { withCredentials: true })
    history.splice(0)
    history.push({ role: 'system', content: '对话已重置，请开始新的咨询' })
  } catch (error) {
    console.error('重置失败:', error)
  } finally {
    isSending.value = false
  }
}

const assessOverall = async () => {
  if (isSending.value) return
  isSending.value = true
  try {
    const response = await axios.post(
      'http://localhost:5000/api/chat/assess',
      { messages: [...history] },
      { withCredentials: true }
    )
    history.push({ role: 'system', content: response.data.assessment })
  } catch (error) {
    console.error('评估失败:', error)
    history.push({ role: 'system', content: '评估服务暂时不可用，请稍后再试' })
  } finally {
    isSending.value = false
  }
}
</script>

<style scoped>
.chat-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 24px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}
.chat-title {
  margin-bottom: 16px;
  font-size: 1.75rem;
  font-weight: bold;
  color: #333;
  text-align: center;
}
.chat-history {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 16px;
  padding: 16px;
  background: #f7f9fc;
  border-radius: 8px;
}
.message {
  margin: 12px 0;
  padding: 12px 16px;
  border-radius: 8px;
  line-height: 1.5;
}
.message.user {
  background: #e1f5fe;
  align-self: flex-end;
  max-width: 70%;
}
.message.assistant {
  background: #f1f1f1;
  align-self: flex-start;
  max-width: 70%;
}
.message.system {
  background: #fff3e0;
  align-self: center;
  max-width: 80%;
  font-style: italic;
}
.role-tag {
  font-size: 0.75rem;
  color: #666;
  margin-bottom: 4px;
}
.input-area {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.input-area textarea {
  width: 100%;
  height: 100px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: none;
  font-size: 1rem;
}
.controls {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}
.btn {
  flex: 1;
  padding: 10px 0;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s ease;
}
.send-btn {
  background: #1976d2;
  color: #fff;
}
.send-btn:disabled {
  background: #90caf9;
  cursor: not-allowed;
}
.reset-btn {
  background: #d32f2f;
  color: #fff;
}
.assess-btn {
  background: #388e3c;
  color: #fff;
}
.btn:hover:not(:disabled) {
  filter: brightness(0.9);
}
</style>