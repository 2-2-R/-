from django.urls import path, include
from rest_framework.routers import DefaultRouter

# ? 核心修复点：确保这里导入了 matrix_heatmap_api
from .views import MajorViewSet, CourseViewSet, CourseSupportViewSet, matrix_heatmap_api

router = DefaultRouter()
router.register(r'majors', MajorViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'supports', CourseSupportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # 专门给热力图提供数据的路由
    path('matrix-heatmap/', matrix_heatmap_api), 
]