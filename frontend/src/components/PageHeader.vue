<!--
  文件名: PageHeader.vue
  编辑时间: 2025-03-14
  代码编写人: Lambert tang
  描述: 页面标题组件，标题、副标题、插槽
-->
<template>
  <div class="page-header">
    <div class="page-header-main">
      <h1 class="page-title">{{ title }}</h1>
      <p v-if="subtitle" class="page-subtitle">{{ subtitle }}</p>
    </div>
    <div v-if="$slots.extra" class="page-header-extra">
      <slot name="extra" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--md-spacing-md);
  margin-bottom: var(--md-spacing-lg);
  flex-wrap: wrap;
}

.page-header-main {
  flex: 1;
  min-width: 0;
}

.page-header-extra {
  flex-shrink: 0;
}

.page-title {
  font: var(--md-typescale-headline-large);
  color: #111827;
  margin: 0 0 var(--md-spacing-xs) 0;
  font-weight: 600;
}

.page-subtitle {
  font: var(--md-typescale-body-medium);
  color: #6b7280;
  margin: 0;
}
</style>
