from django.urls import path
from .views import SchemeVisualizeView, MatrixHeatmapView

urlpatterns = [
    # 完整的访问路径将是 http://127.0.0.1:8000/api/visualize/
    path('visualize/', SchemeVisualizeView.as_view(), name='visualize_scheme'),
    # 矩阵热力图接口
    path('matrix-heatmap/', MatrixHeatmapView.as_view(), name='matrix_heatmap'),
]