<!-- src/views/Register.vue -->
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="w-full max-w-md bg-white p-8 rounded-xl shadow-lg">
      <h2 class="text-2xl font-bold mb-6 text-center">注册</h2>
      <form @submit.prevent="register" class="space-y-4">
        <!-- 用户名 -->
        <div>
          <label class="block mb-1">用户名</label>
          <input
            v-model="username"
            type="text"
            required
            class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-400"
          />
        </div>
        <!-- 邮箱 -->
        <div>
          <label class="block mb-1">电子邮箱</label>
          <input
            v-model="email"
            type="email"
            required
            class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-400"
          />
        </div>
        <!-- 密码 -->
        <div>
          <label class="block mb-1">密码</label>
          <input
            v-model="password"
            type="password"
            required
            class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-400"
          />
        </div>
        <!-- 确认密码 -->
        <div>
          <label class="block mb-1">确认密码</label>
          <input
            v-model="confirm"
            type="password"
            required
            class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-400"
          />
        </div>
        <!-- 错误提示 -->
        <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
        <!-- 提交按钮 -->
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-green-500 text-white py-3 rounded-lg hover:bg-green-600 transition disabled:opacity-50"
        >
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      <!-- 跳转登录 -->
      <p class="mt-4 text-center">
        已有账号？
        <router-link to="/login" class="text-green-500 hover:underline">登录</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Register',
  data() {
    return {
      username: '',
      email: '',
      password: '',
      confirm: '',
      loading: false,
      error: ''
    }
  },
  methods: {
    async register() {
      this.error = ''
      if (this.password !== this.confirm) {
        this.error = '两次密码不一致'
        return
      }
      this.loading = true
      try {
        await axios.post('/api/auth/register', {
          username: this.username,
          email: this.email,
          password: this.password
        })
        this.$router.push('/login')
      } catch (err) {
        this.error = err.response?.data?.message || '注册失败，请重试。'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
/* 可按需调整局部样式 */
</style>
