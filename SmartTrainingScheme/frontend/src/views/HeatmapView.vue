<template>
  <main>
    <section class="stats-section">
       <el-alert title="培养方案概览" type="info" show-icon :closable="false">
          当前专业总学分：{{ totalCredits }}
       </el-alert>
    </section>

    <section class="matrix-section">
      <MatrixHeatmap />
    </section>

    <hr />

    <section class="flow-section">
      <CourseFlow :courses="allCourses" />
    </section>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import MatrixHeatmap from '../components/MatrixHeatmap.vue'
import CourseFlow from '../components/CourseFlow.vue' // 👈 引入你新建的组件

const allCourses = ref([])
const totalCredits = ref(0)

onMounted(async () => {
  // 抓取所有课程数据，用于渲染拓扑图
  const res = await axios.get('http://127.0.0.1:8000/api/courses/')
  allCourses.value = res.data.results
  
  // 计算总学分（自动统计功能）
  totalCredits.value = allCourses.value.reduce((sum, c) => sum + parseFloat(c.credits || 0), 0)
})
</script>

<style scoped>
main {
  padding: 20px;
}
section {
  margin-bottom: 40px;
}
</style>