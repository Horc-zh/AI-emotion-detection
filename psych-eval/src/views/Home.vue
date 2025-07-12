<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-100 to-blue-300 p-4">
    <div class="bg-white/90 backdrop-blur-lg border border-gray-200 rounded-3xl shadow-2xl w-full max-w-2xl p-10">
      <!-- 步骤 1：基本信息收集 -->
      <div class="text-center">
        <h1 class="text-4xl font-extrabold text-gray-800 mb-6">🧠 心理评估系统</h1>
        <p class="text-lg text-gray-600 mb-8">您好，欢迎使用心理评估系统，请问您的性别和年龄是？</p>

        <!-- 性别选择 -->
        <div class="flex justify-center gap-6 mb-6">
          <button
            :class="[
              'px-6 py-3 rounded-full font-semibold transition duration-300',
              gender === 'male' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700 hover:bg-blue-100'
            ]"
            @click="gender = 'male'"
          >
            男性
          </button>
          <button
            :class="[
              'px-6 py-3 rounded-full font-semibold transition duration-300',
              gender === 'female' ? 'bg-pink-500 text-white' : 'bg-gray-200 text-gray-700 hover:bg-pink-100'
            ]"
            @click="gender = 'female'"
          >
            女性
          </button>
        </div>

        <!-- 年龄输入，图标与输入框隔离 -->
        <div class="flex items-center mb-6 space-x-3">
          <span class="text-gray-400 text-xl">🎂</span>
          <input
            type="number"
            v-model.number="age"
            placeholder="请输入年龄"
            class="flex-1 p-4 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>

        <!-- 其他信息输入，图标与输入框隔离 -->
        <div class="flex items-center mb-8 space-x-3">
          <span class="text-gray-400 text-xl">📝</span>
          <input
            type="text"
            v-model="otherInfo"
            placeholder="请输入其他信息（可选）"
            class="flex-1 p-4 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>

        <!-- 下一步按钮 -->
        <button
          :disabled="!gender || age === null"
          @click="nextStep"
          class="w-full bg-blue-500 hover:bg-blue-600 text-white py-3 rounded-xl transition duration-300 disabled:opacity-50"
        >
          下一步
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      gender: '',
      age: null,
      otherInfo: '' // 新增字段：其他信息
    };
  },
  methods: {
    nextStep() {
      // 带上年龄、性别及其他信息，通过 query 传递给下一个页面
      const query = { age: this.age, gender: this.gender, otherInfo: this.otherInfo };
      if (this.age < 18) {
        this.$router.push({ name: 'Children', query });
      } else {
        this.$router.push({ name: 'Adult', query });
      }
    }
  }
};
</script>

<style scoped>
/* 如需定制可在此添加样式 */
</style>
