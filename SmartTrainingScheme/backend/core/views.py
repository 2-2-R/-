from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from django.db.models import Sum, Count

from .models import Major, Course, CourseSupport, IndicatorPoint
from .serializers import MajorSerializer, CourseSerializer, CourseSupportSerializer

class MajorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Major.objects.all()
    serializer_class = MajorSerializer

    # 👇 新增这个 stats 接口，访问路径会变成 /api/majors/{id}/stats/
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        major = self.get_object()
        
        # 1. 按“学期”分组，自动统计每个学期的总学分和课程数量
        # 注意：这里假设你的 Course 模型里有 semester(学期) 和 credits(学分) 字段
        semester_stats = Course.objects.filter(major=major).values('semester').annotate(
            total_credits=Sum('credits'),
            course_count=Count('id')
        ).order_by('semester')
        
        # 2. 计算整个专业的总学分
        total_major_credits = Course.objects.filter(major=major).aggregate(
            sum_credits=Sum('credits')
        )['sum_credits'] or 0

        # 把计算好的数据打包发给前端
        return Response({
            "major_name": major.name,
            "total_credits": total_major_credits,
            "semester_distribution": semester_stats
        })

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    # 达成度计算逻辑：访问 /api/courses/{id}/calculate/
    @action(detail=True, methods=['post'])
    def calculate(self, request, pk=None):
        course = self.get_object()
        score = request.data.get('score', 0)
        supports = CourseSupport.objects.filter(course=course)
        results = []
        for s in supports:
            attainment = (float(score) / 100.0) * float(s.weight)
            results.append({
                "indicator": s.indicator.id,
                "attainment": attainment
            })
        return Response(results)

# 🎯 确保这个类的名字和 urls.py 里的一模一样
class CourseSupportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CourseSupport.objects.all()
    serializer_class = CourseSupportSerializer

@api_view(['GET'])
def matrix_heatmap_api(request):
    """专门为前端热力图提供整合数据的接口"""
    # 1. 抓取所有指标点 (🎯 修复点：用 sequence 替代 number)
    indicators = []
    for ind in IndicatorPoint.objects.all():
        indicators.append({
            'id': ind.id,
            'number': ind.sequence,  # 👈 你的数据库里叫 sequence
            'content': ind.content
        })
    
    # 2. 抓取所有课程
    courses = Course.objects.all().values('id', 'name') 
    
    # 3. 抓取所有的支撑关系 (🎯 增加容错：自动识别外键名字)
    supports = CourseSupport.objects.all()
    support_matrix = []
    for s in supports:
        # 尝试获取指标点的 ID（兼容 indicator 或 indicator_point 两种常见命名）
        indicator_id = None
        if hasattr(s, 'indicator_point') and s.indicator_point:
            indicator_id = s.indicator_point.id
        elif hasattr(s, 'indicator') and s.indicator:
            indicator_id = s.indicator.id

        support_matrix.append({
            'course_id': s.course.id if hasattr(s, 'course') and s.course else None,
            'indicator_point_id': indicator_id, 
            'weight': s.weight
        })

    # 打包成 Vue 期待的格式
    return Response({
        'indicator_points': indicators,
        'courses': list(courses),
        'support_matrix': support_matrix
    })