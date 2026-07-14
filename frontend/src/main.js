/**
 * 前端入口文件
 * ===========
 * 这是整个前端应用的起点，做了以下几件事：
 *
 * 1. 创建 Vue 应用实例
 * 2. 挂载 Pinia（状态管理，类似 Vuex，但更简洁）
 * 3. 挂载 Element Plus（UI组件库，提供按钮、表格、弹窗等）
 * 4. 挂载 Vue Router（路由，控制页面跳转）
 * 5. 将应用挂载到 HTML 的 #app 元素上
 *
 * 每个插件的作用：
 * - Pinia：全局状态管理，多个组件共享数据
 * - Element Plus：提供丰富的UI组件，不用自己写样式
 * - Router：根据URL显示不同页面
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'  // Element Plus 的CSS样式

import App from './App.vue'  // 根组件
import router from './router'  // 路由配置

const app = createApp(App)
app.use(createPinia())  // 状态管理
app.use(ElementPlus)    // UI组件库
app.use(router)         // 路由
app.mount('#app')       // 挂载到HTML的<div id="app">