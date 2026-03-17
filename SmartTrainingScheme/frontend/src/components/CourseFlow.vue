<template>
  <div class="flow-chart-wrapper">
    <div ref="mermaidTarget" class="mermaid-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import mermaid from 'mermaid'

// 接收父组件传过来的课程列表数据
const props = defineProps({
  courses: {
    type: Array,
    required: true
  }
})

const mermaidTarget = ref(null)

// 核心逻辑：将课程的先修关系转化为 Mermaid 语法
const renderChart = async () => {
  if (!props.courses || props.courses.length === 0) return

  // 1. 初始化 Mermaid 语法头部：graph LR 表示从左往右画图
  let graphDefinition = 'graph LR\n'
  
  // 2. 遍历课程，生成节点和连线
  props.courses.forEach(course => {
    // 定义节点：C+ID[课程名称]
    graphDefinition += `  C${course.id}["${course.name}"]\n`
    
    // 如果有先修课字段（假设字段名为 prerequisites，存储的是先修课ID列表）
    if (course.prerequisites && Array.isArray(course.prerequisites)) {
      course.prerequisites.forEach(preId => {
        graphDefinition += `  C${preId} --> C${course.id}\n`
      })
    }
  })

  // 3. 渲染图片
  const { render } = mermaid
  const { svg } = await render(`mermaid-${Math.random().toString(36).substr(2, 9)}`, graphDefinition)
  mermaidTarget.value.innerHTML = svg
}

onMounted(() => {
  mermaid.initialize({ startOnLoad: false, theme: 'neutral' })
  renderChart()
})

// 当数据发生变化时（比如老师修改了先修关系），自动重画
watch(() => props.courses, () => renderChart(), { deep: true })
</script>

<style scoped>
.flow-chart-wrapper {
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
  overflow: auto;
}
.mermaid-container {
  display: flex;
  justify-content: center;
}
</style>