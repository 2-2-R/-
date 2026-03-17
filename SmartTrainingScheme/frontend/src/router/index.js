import { createRouter, createWebHistory } from 'vue-router'
// 引入咱们刚才辛苦写好的组件
import MatrixHeatmap from '../components/MatrixHeatmap.vue'

const routes = [
  {
    path: '/', // 默认首页
    name: 'Home',
    component: MatrixHeatmap // ? 把热力图作为首页显示
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router