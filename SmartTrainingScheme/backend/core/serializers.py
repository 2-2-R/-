# core/serializers.py
from rest_framework import serializers
from .models import Major, Course
from .models import Major, Course, CourseSupport, IndicatorPoint

class MajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = '__all__'  # 懒人写法：把专业表的所有字段都暴露出出去

class CourseSerializer(serializers.ModelSerializer):
    # 给课程额外加一个字段，把专业的中文名字带出来，方便前端显示
    major_name = serializers.CharField(source='major.name', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'credits', 'major_name']

class CourseSupportSerializer(serializers.ModelSerializer):
    course_name = serializers.ReadOnlyField(source='course.name')
    # ? 核心修复点：把这里的 source 指向正确的模型字段名
    # 如果你的 models.py 里定义的字段名是 indicator，就用 indicator
    indicator_detail = serializers.ReadOnlyField(source='indicator.content') 

    class Meta:
        model = CourseSupport
        # ? 确保这里的 fields 列表里包含的是模型中真实存在的字段名
        # 请检查你的 models.py，如果是 indicator 就写 indicator，如果是 indicator_point 就写它
        fields = ['id', 'course', 'course_name', 'indicator', 'indicator_detail', 'weight']