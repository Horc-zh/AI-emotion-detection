// src/main.js
import { createApp } from 'vue'
import { createPinia }  from 'pinia'                  // 1. 引入 Pinia
import axios           from 'axios'
import App             from './App.vue'
import router          from './router'

// 2. 只需一次加载 Tailwind v4 主样式文件
import '@/assets/tailwind.css'

// 3. 全局配置 Axios 默认值
axios.defaults.baseURL        = 'http://localhost:5000'  // 所有相对 URL 会拼成 http://localhost:5000/<path> :contentReference[oaicite:3]{index=3}
axios.defaults.withCredentials = true                   // 跨域请求时自动携带 Cookie 等凭据 :contentReference[oaicite:4]{index=4}

// 4. 创建应用实例并注册插件
const app = createApp(App)

// 5. 将 Axios 挂载为全局属性，组件里可通过 this.$axios 访问 :contentReference[oaicite:5]{index=5}
app.config.globalProperties.$axios = axios

app.use(createPinia())  // 注册 Pinia
app.use(router)         // 注册 Router

app.mount('#app')
