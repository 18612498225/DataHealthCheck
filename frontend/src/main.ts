/**
 * 文件名: main.ts
 * 编辑时间: 2025-03-14
 * 代码编写人: Lambert tang
 * 描述: Vue 应用入口，挂载路由与 Element Plus
 */
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/global.css'
import './styles/element-overrides.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.mount('#app')
