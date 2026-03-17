import { createApp } from 'vue'
import App from './App.vue'

// 1. 引入我们刚刚写的路由
import router from './router' 

// 2. 引入 Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)

// 3. 告诉 Vue：使用路由！使用组件库！
app.use(router)     // ? 这一行解决了你的报错！
app.use(ElementPlus)

app.mount('#app')