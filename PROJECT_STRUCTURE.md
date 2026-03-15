git add .
git commit -m "我的描述"
git config --global --unset http.proxy
git push -u origin main --force


# 面向专业认证的本科培养方案智能设计系统 - 项目目录结构建议

该目录结构基于 **Django + Vue3 (Vite)** 技术栈设计，专为支持 OBE 认证逻辑与图形化编排功能优化。

## ? 顶层目录概览

```text
SmartTrainingScheme/
├── backend/                  # Django 后端根目录
│   ├── config/               # 项目全局配置 (settings, urls, wsgi)
│   ├── api/                  # 统一对外接口层 (DRF Views, Serializers)
│   ├── core/                 # 核心业务数据模型 (Models for 培养方案, 课程等)
│   ├── logic_engine/         # [核心亮点] 图论与规则校验引擎
│   ├── manage.py             # Django 管理脚本
│   └── requirements.txt      # Python 依赖列表
├── frontend/                 # Vue3 + Vite 前端根目录
│   ├── public/               # 静态资源
│   ├── src/
│   │   ├── api/              # Axios 请求封装
│   │   ├── assets/           # 静态资源 (Images, CSS)
│   │   ├── components/       # 可视化组件 (AntV X6 封装, 拖拽组件)
│   │   ├── views/            # 页面视图 (培养方案管理, 矩阵编辑等)
│   │   ├── router/           # Vue Router 路由配置
│   │   ├── stores/           # Pinia 状态管理
│   │   └── App.vue           # 根组件
│   ├── index.html            # 入口 HTML
│   ├── package.json          # Node 依赖列表
│   └── vite.config.js        # Vite 配置
└── docs/                     # 项目文档 (需求说明, 数据库设计)
```

---

## ?? 详细模块说明

### 1. 后端 (Backend)

#### `core/` (基础业务模块)
存放与数据库直接交互的 Models 和基础 Service。
- `models.py`: 定义 `TrainingProgram` (培养方案), `Course` (课程), `GraduationRequirement` (毕业要求), `IndicatorPoint` (指标点)。
- `services.py`: 基础的 CRUD 逻辑。

#### `api/` (接口层)
基于 Django REST Framework，负责处理 HTTP 请求与响应。
- `serializers.py`: 数据序列化。
- `urls.py`: 路由分发。
- `views.py`: 视图逻辑。

#### `logic_engine/` (? 核心亮点)
**存放本项目最核心的算法逻辑，与普通 CRUD 业务解耦。**
- `graph_builder.py`: 使用 **NetworkX** 构建课程体系的有向无环图 (DAG)。
- `validator.py`: 执行拓扑排序，检测“逻辑死锁”和“时序错误”。
- `obe_calculator.py`: 计算指标点支撑度权重，生成分析报告。
- `nlp_processor.py`: (预留) 接入 Ollama/NLP 模型进行文本规范性审查。

### 2. 前端 (Frontend)

#### `src/components/`
- `GraphEditor/`: 封装 **AntV X6** 或 **ECharts** 的图形化编排组件（课程拓扑图）。
- `MatrixTable/`: 复杂的支撑矩阵录入表格（毕业要求 vs 课程）。

#### `src/views/`
- `Dashboard/`: 仪表盘。
- `SchemeDesign/`: 培养方案设计主工作台。
- `CourseLibrary/`: 公共课程资源池管理。

---

## ? 快速开始建议

1. **后端初始化**:
   ```bash
   cd backend
   django-admin startproject config .
   python manage.py startapp core
   python manage.py startapp api
   # 手动创建 logic_engine 包
   ```

2. **前端初始化**:
   ```bash
   npm create vite@latest frontend -- --template vue
   cd frontend
   npm install ant-design-vue @antv/x6 axios pinia vue-router
   ```
