<!-- src/views/Adult.vue -->
<template>
  <div class="flex min-h-screen">
    <!-- 深色侧边栏 -->
    <aside class="w-64 bg-blue-800 text-white flex flex-col">
      <div class="px-6 py-5 text-2xl font-bold border-b border-blue-700">
        心理测评
      </div>
      <nav class="flex-1 overflow-y-auto">
        <ul>
          <li v-for="mode in modes" :key="mode.value">
            <button
              @click="selected = mode.value"
              :class="[
                'w-full flex items-center px-6 py-3 transition-colors duration-200',
                selected === mode.value
                  ? 'bg-blue-700 text-white'
                  : 'hover:bg-blue-700 text-white'
              ]"
            >
              <span class="mr-3 text-xl">{{ mode.icon }}</span>
              <span class="font-medium">{{ mode.label }}</span>
            </button>
          </li>
        </ul>
      </nav>
      <!-- 底部信息 -->
      <div class="px-6 py-4 text-sm border-t border-blue-700">
        <div class="flex justify-between items-center">
          <span>版本 1.0</span>
          <button
            @click="logout"
            class="text-white hover:underline text-sm"
          >
            退出
          </button>
        </div>
      </div>
    </aside>

    <!-- 卡片式主内容区 -->
    <main class="flex-1 bg-gray-100 p-8 overflow-auto">
      <!-- 概览 -->
      <div
        v-if="selected === 'overview'"
        class="bg-white rounded-xl p-6 shadow space-y-4"
      >
        <h2 class="text-2xl font-bold">🧑‍🎓 成年人评估概览</h2>
        <p>年龄：{{ age }} 岁</p>
        <p>性别：{{ gender === 'male' ? '男性' : '女性' }}</p>
        <!-- 只有当 otherInfo 非空时才显示 -->
        <p v-if="otherInfo">其他信息：{{ otherInfo }}</p>
      </div>

      <!-- 文本描述评估 -->
      <div
        v-else-if="selected === 'text'"
        class="bg-white rounded-xl p-6 shadow space-y-4"
      >
        <ChatEval />
      </div>

      <!-- 问卷评估 -->
      <div
        v-else-if="selected === 'survey'"
        class="bg-white rounded-xl p-6 shadow space-y-4"
      >
        <SurveyForm :ageGroup="'adult'" :gender="gender" />
      </div>

      <!-- 画图评估 -->
      <div
        v-else-if="selected === 'image'"
        class="bg-white rounded-xl p-6 shadow space-y-4"
      >
        <ImageEval />
      </div>

      <!-- 综合评估 -->
      <div
        v-else-if="selected === 'evaluate'"
        class="bg-white rounded-xl p-6 shadow space-y-4"
      >
        <Evaluate :ageGroup="'adult'" :gender="gender" />
      </div>
    </main>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ChatEval from '@/views/Chat.vue'
import SurveyForm from '@/views/Survey.vue'
import ImageEval from '@/views/Image.vue'
import Evaluate from '@/views/Evaluate.vue'

export default {
  name: 'Adult',
  props: {
    age: {
      type: Number,
      required: true
    },
    gender: {
      type: String,
      required: true
    },
    otherInfo: {
      type: String,
      default: '' // 当父组件未传入时，默认为空字符串
    }
  },
  components: {
    ChatEval,
    SurveyForm,
    ImageEval,
    Evaluate
  },
  data() {
    return {
      selected: 'overview',
      modes: [
        { label: '概览',     value: 'overview', icon: '🧑‍🎓' },
        { label: '文本描述', value: 'text',     icon: '💬'   },
        { label: '填写问卷', value: 'survey',   icon: '📝'   },
        { label: '画图评估', value: 'image',    icon: '🖼️'  },
        { label: '综合评估', value: 'evaluate', icon: '🔀'   }
      ]
    }
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const logout = () => {
      // 清除认证状态
      authStore.logout()
      // 跳转到登录页面
      router.replace({ name: 'Login' })
    }

    return {
      logout
    }
  }
}
</script>

<style scoped>
/* 可根据需要补充或覆盖局部样式 */
</style>
