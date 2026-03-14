<!--
  文件名: App.vue
  编辑时间: 2025-03-14
  代码编写人: Lambert tang
  描述: 根组件，配置 Element Plus 中文与路由视图
-->
<template>
  <el-config-provider :locale="zhCn">
    <router-view />
  </el-config-provider>
</template>

<script setup lang="ts">
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
</script>
