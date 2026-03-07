import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',        // 当访问根路径时
    redirect: '/heatmap'  // 自动跳转到 /heatmap
  },
  {
    path: '/heatmap',
    name: 'heatmap',
    component: () => import('../views/HeatmapView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router