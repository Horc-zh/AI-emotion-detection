<!-- src/views/Login.vue -->
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="w-full max-w-md bg-white p-8 rounded-xl shadow-lg">
      <h2 class="text-2xl font-bold mb-6 text-center">登录</h2>
      <form @submit.prevent="login" class="space-y-4">
        <!-- 邮箱 -->
        <div>
          <label class="block mb-1">电子邮箱</label>
          <input
            v-model="email"
            type="email"
            required
            class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-400"
          />
        </div>
        <!-- 密码 -->
        <div>
          <label class="block mb-1">密码</label>
          <input
            v-model="password"
            type="password"
            required
            class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-400"
          />
        </div>
        <!-- 记住我 -->
        <div class="flex items-center">
          <input v-model="remember" id="remember" type="checkbox" class="mr-2"/>
          <label for="remember">记住我</label>
        </div>
        <!-- 错误提示 -->
        <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
        <!-- 提交按钮 -->
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-500 text-white py-3 rounded-lg hover:bg-blue-600 transition disabled:opacity-50"
        >
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      <!-- 跳转注册 -->
      <p class="mt-4 text-center">
        没有账号？
        <router-link to="/register" class="text-blue-500 hover:underline">注册</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      remember: false,
      loading: false,
      error: ''
    }
  },
  methods: {
    async login() {
      this.error = ''
      this.loading = true
      try {
        const { data } = await axios.post('/api/auth/login', {
          email: this.email,
          password: this.password
        })
        // 存储 token
        const authStore = useAuthStore()
        authStore.setToken(data.token)
        // 可选：本地存储
        if (this.remember) localStorage.setItem('token', data.token)
        // 重定向
        const redirectPath = this.$route.query.redirect || '/'
        this.$router.push(redirectPath)
      } catch (err) {
        this.error = err.response?.data?.message || '登录失败，请重试。'
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

