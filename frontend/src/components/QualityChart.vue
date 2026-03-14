<!--
  文件名: QualityChart.vue
  编辑时间: 2025-03-14
  代码编写人: Lambert tang
  描述: 质量通过/失败饼图组件（ECharts）
-->
<template>
  <div ref="chartRef" style="width: 100%; height: 200px" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  passed: number
  failed: number
  title?: string
}>()

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

function render() {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)
  chart.setOption({
    title: {
      text: props.title || '检查结果',
      left: 'center',
      textStyle: { fontSize: 14, fontWeight: 500, color: '#374151' },
    },
    tooltip: { trigger: 'item' },
    color: ['#2e7d32', '#c62828'],
    series: [{
      type: 'pie',
      radius: ['45%', '70%'],
      center: ['50%', '55%'],
      data: [
        { value: props.passed, name: '通过' },
        { value: props.failed, name: '失败' },
      ],
      label: { show: true, fontSize: 12 },
      emphasis: { scale: true },
    }],
  })
}

onMounted(render)
watch(() => [props.passed, props.failed], render)
</script>
