// src/router/index.js

import { createRouter, createWebHistory } from 'vue-router'
import Home      from '@/views/Home.vue'
import Login     from '@/views/Login.vue'
import Register  from '@/views/Register.vue'
import Children  from '@/views/Children.vue'
import Adult     from '@/views/Adult.vue'
import ChatEval  from '@/views/Chat.vue'
import Survey    from '@/views/Survey.vue'
import ImageEval from '@/views/Image.vue'
import Evaluate  from '@/views/Evaluate.vue'
import Report from '@/views/Report.vue' 
// 引入 Pinia 的认证状态管理
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }  // 需要登录
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    props: route => ({
      redirect: route.query.redirect || '/'
    }),
    meta: { guest: true }  // 仅访客可访问
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { guest: true }  // 仅访客可访问
  },
  {
    path: '/children',
    name: 'Children',
    component: Children,
    props: route => ({
      age:        Number(route.query.age),
      gender:     route.query.gender,
      otherInfo:  route.query.otherInfo || ''
    }),
    meta: { requiresAuth: true }  // 需要登录
  },
  {
    path: '/adult',
    name: 'Adult',
    component: Adult,
    props: route => ({
      age:        Number(route.query.age),
      gender:     route.query.gender,
      otherInfo:  route.query.otherInfo || ''
    }),
    meta: { requiresAuth: true }  // 需要登录
  },
  {
    path: '/chat',
    name: 'Chat',
    component: ChatEval,
    meta: { requiresAuth: true }  // 需要登录
  },
  {
    path: '/survey/:ageGroup/:gender',
    name: 'Survey',
    component: Survey,
    props: true,
    meta: { requiresAuth: true }  // 需要登录
  },
  {
    path: '/image',
    name: 'Image',
    component: ImageEval,
    meta: { requiresAuth: true }  // 需要登录
  },
  {
    path: '/evaluate/:ageGroup/:gender',
    name: 'EvaluateWithParams',
    component: Evaluate,
    props: true,
    meta: { requiresAuth: true }  // 需要登录
  },
  {
    path: '/report',
    name: 'Report',
    component: Report,
    props: route => ({
      report: route.query.report ? decodeURIComponent(route.query.report) : ''
    }),
    meta: { requiresAuth: true }  // 需要登录才能查看报告
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局导航守卫：拦截未授权访问并处理登录后重定向
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const loggedIn = !!authStore.token  // 判断用户是否已登录

  if (to.meta.requiresAuth && !loggedIn) {
    // 如果路由需要登录且用户未登录，重定向到登录页，并记录原始目标路径
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.meta.guest && loggedIn) {
    // 如果路由为访客页且用户已登录，重定向到主页
    next({ name: 'Home' })
  } else {
    // 允许访问
    next()
  }
})

export default router
