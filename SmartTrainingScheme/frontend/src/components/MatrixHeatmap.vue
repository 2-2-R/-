<template>
  <div class="heatmap-container">
    <h2>人才培养支撑矩阵热力图</h2>
    <div v-if="loading">Loading...</div>
    <div v-if="error">{{ error }}</div>
    <div v-if="chartData" class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th class="sticky-col">课程</th>
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
              <td class="sticky-col">{{ course.name }}</td>
              <td
                v-for="indicator in chartData.indicator_points"
                :key="indicator.id"
                :style="{ backgroundColor: getCellColor(course.id, indicator.id) }"
                class="heatmap-cell"
                @mouseover="showTooltip(course, indicator, $event)"
                @mouseleave="hideTooltip"
              ></td>
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
      <div><strong>课程:</strong> {{ tooltip.courseName }}</div>
      <div><strong>指标点:</strong> {{ tooltip.indicatorContent }}</div>
      <div><strong>权重:</strong> {{ tooltip.weight }}</div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';

export default {
  name: 'MatrixHeatmap',
  setup() {
    const chartData = ref(null);
    const loading = ref(true);
    const error = ref(null);
    const tooltip = ref({
      visible: false,
      courseName: '',
      indicatorContent: '',
      weight: 0,
      x: 0,
      y: 0,
    });

    const fetchData = async () => {
      try {
        const response = await axios.get('/api/matrix-heatmap/');
        chartData.value = response.data;
      } catch (err) {
        error.value = 'Failed to fetch data. Please try again later.';
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    onMounted(fetchData);

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

    const getCellColor = (courseId, indicatorId) => {
      if (!chartData.value) return '#f0f0f0';
      const support = chartData.value.support_matrix.find(
        (s) => s.course_id === courseId && s.indicator_point_id === indicatorId
      );
      if (!support) return '#f0f0f0'; // Light Grey for no support

      const weight = support.weight;
      if (weight >= 0.5) return '#1e3a8a'; // Deep Blue
      if (weight >= 0.3) return '#3b82f6'; // Medium Blue
      if (weight > 0) return '#bfdbfe';   // Light Blue (instead of grey for 0.1)
      
      return '#f0f0f0'; // Default
    };

    const showTooltip = (course, indicator, event) => {
      const support = chartData.value.support_matrix.find(
        (s) => s.course_id === course.id && s.indicator_point_id === indicator.id
      );
      tooltip.value = {
        visible: true,
        courseName: course.name,
        indicatorContent: indicator.content,
        weight: support ? support.weight : 'N/A',
        x: event.clientX + 15,
        y: event.clientY + 15,
      };
    };

    const hideTooltip = () => {
      tooltip.value.visible = false;
    };

    return {
      chartData,
      loading,
      error,
      groupedCourses,
      getCellColor,
      tooltip,
      showTooltip,
      hideTooltip,
    };
  },
};
</script>

<style scoped>
.heatmap-container {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  margin: 2rem;
}
.table-wrapper {
  overflow-x: auto;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  max-height: 80vh;
}
table {
  width: 100%;
  border-collapse: collapse;
  text-align: center;
}
th, td {
  border: 1px solid #e2e8f0;
  padding: 0.75rem;
  min-width: 80px;
}
thead th {
  background-color: #f8fafc;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 2;
}
.sticky-col {
  background-color: white !important; /* 确保背景是不透明的 */
  color: #333;
}
thead .sticky-col {
    z-index: 3;
}
.category-row {
  text-align: left;
  background-color: #f1f5f9;
  font-weight: bold;
  position: sticky;
  top: 50px; /* Adjust based on header height */
  z-index: 2;
}
.heatmap-cell {
  width: 80px;
  height: 40px;
  cursor: pointer;
  transition: transform 0.2s;
}
.heatmap-cell:hover {
    transform: scale(1.1);
    box-shadow: 0 0 10px rgba(0,0,0,0.3);
}
.tooltip {
  position: fixed;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 10px 15px;
  border-radius: 5px;
  font-size: 0.9rem;
  pointer-events: none;
  z-index: 100;
  max-width: 300px;
}
</style>
