/**
 * 文件名: vite-env.d.ts
 * 编辑时间: 2025-03-14
 * 代码编写人: Lambert tang
 * 描述: Vite 与 Vue 类型声明
 */
/// <reference types="vite/client" />
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, unknown>
  export default component
}
