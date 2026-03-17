<template>
  <div class="heatmap-container">
    <h2>人才培养支撑矩阵热力图</h2>

    <div class="stats-dashboard" v-if="majorStats">
      <div class="stat-card highlight">
        <div class="stat-title">专业总学分</div>
        <div class="stat-value">{{ majorStats.total_credits }}</div>
      </div>
      
      <div class="stat-card" v-for="(stat, index) in majorStats.semester_distribution" :key="index">
        <div class="stat-title">第 {{ stat.semester }} 学期</div>
        <div class="stat-value">{{ stat.total_credits }} <span class="unit">学分</span></div>
        <div class="stat-desc">共 {{ stat.course_count }} 门课</div>
      </div>
    </div>

    <div v-if="loading">加载中...</div>
    <div v-if="error" class="error-msg">{{ error }}</div>
    
    <div v-if="chartData" class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th class="sticky-col">课程名称</th>
            <th v-for="indicator in chartData.indicator_points" :key="indicator.id">
              {{ indicator.number }}
            </th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(group, category) in groupedCourses" :key="category">
            <tr>
              <td class="category-row sticky-col" :colspan="chartData.indicator_points.length + 1">
                {{ category }}
              </td>
            </tr>
            <tr v-for="course in group" :key="course.id">
              <td class="sticky-col course-name-cell">{{ course.name }}</td>
              <td
                v-for="indicator in chartData.indicator_points"
                :key="indicator.id"
                :style="{ backgroundColor: getCellColor(course.id, indicator.id) }"
                class="heatmap-cell"
                @mouseover="showTooltip(course, indicator, $event)"
                @mouseleave="hideTooltip"
              >
                <span class="cell-label">{{ getWeightLabel(course.id, indicator.id) }}</span>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <div
      v-if="tooltip.visible"
      class="tooltip"
      :style="{ top: tooltip.y + 'px', left: tooltip.x + 'px' }"
    >
      <div class="tooltip-item"><strong>课程:</strong> {{ tooltip.courseName }}</div>
      <div class="tooltip-item"><strong>指标点:</strong> {{ tooltip.indicatorContent }}</div>
      <div class="tooltip-item">
        <strong>支撑强度:</strong> 
        <span :class="'level-' + tooltip.level">{{ tooltip.level }}</span> 
        ({{ tooltip.weight }})
      </div>
      <hr class="tooltip-divider" />
      <div class="tooltip-desc">{{ tooltip.description }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';

// === 1. 定义所有数据源 ===
const majorStats = ref(null);
const chartData = ref(null);
const loading = ref(true);
const error = ref(null);

const tooltip = ref({
  visible: false,
  courseName: '',
  indicatorContent: '',
  weight: 0,
  level: '',
  description: '',
  x: 0,
  y: 0,
});

// === 2. 核心网络请求 ===
const fetchStats = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/majors/31/stats/');
    majorStats.value = response.data;
  } catch (err) {
    console.error('统计数据获取失败:', err);
  }
};

const fetchData = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/matrix-heatmap/');
    chartData.value = response.data;
  } catch (err) {
    error.value = '无法获取矩阵数据，请检查后端 API。';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

// 页面加载时同时触发两个请求
onMounted(() => {
  fetchData();
  fetchStats();
});

// === 3. 业务逻辑计算 ===
const groupedCourses = computed(() => {
  if (!chartData.value) return {};
  return chartData.value.courses.reduce((acc, course) => {
    const category = course.category || '未分类';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(course);
    return acc;
  }, {});
});

const getWeightInfo = (weight) => {
  if (weight >= 0.5) return { label: 'H', desc: '高度支撑：对该指标点达成起决定作用' };
  if (weight >= 0.3) return { label: 'M', desc: '中度支撑：有较强关联性' };
  if (weight > 0) return { label: 'L', desc: '弱支撑：仅作为辅助性支撑' };
  return { label: '', desc: '无支撑关系' };
};

const getCellColor = (courseId, indicatorId) => {
  if (!chartData.value) return '#f0f0f0';
  const support = chartData.value.support_matrix.find(
    (s) => s.course_id === courseId && s.indicator_point_id === indicatorId
  );
  if (!support) return '#ffffff';

  const weight = support.weight;
  if (weight >= 0.5) return '#1e3a8a'; 
  if (weight >= 0.3) return '#3b82f6'; 
  return '#bfdbfe';                  
};

const getWeightLabel = (courseId, indicatorId) => {
  if (!chartData.value) return '';
  const support = chartData.value.support_matrix.find(
    (s) => s.course_id === courseId && s.indicator_point_id === indicatorId
  );
  return support ? getWeightInfo(support.weight).label : '';
};

// === 4. Tooltip 悬浮交互 ===
const showTooltip = (course, indicator, event) => {
  const support = chartData.value.support_matrix.find(
    (s) => s.course_id === course.id && s.indicator_point_id === indicator.id
  );
  
  const weight = support ? support.weight : 0;
  const info = getWeightInfo(weight);

  tooltip.value = {
    visible: true,
    courseName: course.name,
    indicatorContent: indicator.content,
    weight: weight || 'N/A',
    level: info.label || '无',
    description: info.desc,
    x: event.clientX + 15,
    y: event.clientY + 15,
  };
};

const hideTooltip = () => {
  tooltip.value.visible = false;
};
</script>

<style scoped>
/* 原有矩阵样式 */
.heatmap-container {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  margin: 1.5rem;
}
.table-wrapper {
  overflow: auto;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  max-height: 85vh;
}
table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  text-align: center;
}
th, td {
  border: 1px solid #e2e8f0;
  padding: 0.5rem;
  min-width: 60px;
}
thead th {
  background-color: #f8fafc;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 10;
}
.sticky-col {
  position: sticky;
  left: 0;
  background-color: white !important;
  z-index: 5;
  border-right: 2px solid #cbd5e1;
  text-align: left;
  min-width: 180px;
}
thead .sticky-col {
  z-index: 15;
}
.category-row {
  background-color: #e2e8f0 !important;
  font-weight: bold;
  text-align: left;
}
.course-name-cell {
  font-size: 0.9rem;
  color: #334155;
}
.heatmap-cell {
  position: relative;
  cursor: help;
  transition: all 0.2s;
}
.cell-label {
  font-size: 0.75rem;
  color: rgba(255,255,255,0.8);
  font-weight: bold;
}
.heatmap-cell:hover {
  filter: brightness(1.2);
  box-shadow: inset 0 0 5px rgba(0,0,0,0.2);
}

/* Tooltip 样式 */
.tooltip {
  position: fixed;
  background-color: rgba(15, 23, 42, 0.95);
  color: #f8fafc;
  padding: 12px 16px;
  border-radius: 6px;
  font-size: 0.85rem;
  pointer-events: none;
  z-index: 9999;
  max-width: 280px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
  line-height: 1.5;
}
.tooltip-item {
  margin-bottom: 4px;
}
.tooltip-divider {
  border: 0;
  border-top: 1px solid #475569;
  margin: 8px 0;
}
.tooltip-desc {
  color: #94a3b8;
  font-style: italic;
}
.level-H { color: #f87171; font-weight: bold; }
.level-M { color: #fbbf24; font-weight: bold; }
.level-L { color: #60a5fa; font-weight: bold; }
.error-msg { color: #ef4444; padding: 1rem; }

/* 🎯 修复：将看板样式安全地包裹在 style 标签内部 */
.stats-dashboard {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  overflow-x: auto;
  padding-bottom: 10px;
}
.stat-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 15px 20px;
  min-width: 120px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.stat-card.highlight {
  background: #eff6ff;
  border-color: #bfdbfe;
}
.stat-card.highlight .stat-value {
  color: #1d4ed8;
}
.stat-title {
  font-size: 0.85rem;
  color: #64748b;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #334155;
}
.unit {
  font-size: 0.8rem;
  font-weight: normal;
  color: #94a3b8;
}
.stat-desc {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 5px;
}
</style>