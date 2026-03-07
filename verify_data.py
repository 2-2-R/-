#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证"物联网工程专业.xlsx"数据是否已导入数据库
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'SmartTrainingScheme', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import (
    Major, TrainingObjective, GraduationRequirement, 
    ObjectiveSupport, IndicatorPoint, Course, CourseSupport
)

def verify_data():
    """验证数据库中的数据"""
    print("=" * 80)
    print("开始验证数据库中的数据...")
    print("=" * 80)
    
    # 1. 检查专业
    print("\n【1. 专业信息】")
    majors = Major.objects.all()
    print(f"数据库中共有 {majors.count()} 个专业")
    for major in majors:
        print(f"  - {major.name} ({major.code})")
    
    # 查找物联网工程专业
    iot_major = Major.objects.filter(name__contains="物联网").first()
    if not iot_major:
        print("\n? 未找到物联网工程专业数据！")
        return False
    
    print(f"\n? 找到专业: {iot_major.name} ({iot_major.code})")
    
    # 2. 检查培养目标
    print("\n【2. 培养目标】")
    objectives = TrainingObjective.objects.filter(major=iot_major)
    print(f"该专业共有 {objectives.count()} 个培养目标")
    for obj in objectives:
        print(f"  目标{obj.sequence}: {obj.content[:50]}...")
    
    # 3. 检查毕业要求
    print("\n【3. 毕业要求】")
    requirements = GraduationRequirement.objects.filter(major=iot_major)
    print(f"该专业共有 {requirements.count()} 个毕业要求")
    for req in requirements:
        print(f"  毕业要求{req.sequence}: {req.content[:50]}...")
        
        # 检查该毕业要求的指标点
        indicators = IndicatorPoint.objects.filter(requirement=req)
        print(f"    └─ 包含 {indicators.count()} 个指标点")
        for ind in indicators:
            print(f"       指标点{req.sequence}.{ind.sequence} (权重: {ind.weight})")
    
    # 4. 检查培养目标支持关系
    print("\n【4. 培养目标支持关系】")
    obj_supports = ObjectiveSupport.objects.filter(requirement__major=iot_major)
    print(f"共有 {obj_supports.count()} 条培养目标支持关系")
    if obj_supports.count() > 0:
        print("  示例:")
        for support in obj_supports[:5]:
            print(f"  - 毕业要求{support.requirement.sequence} -> 目标{support.objective.sequence} (权重: {support.weight})")
    
    # 5. 检查课程
    print("\n【5. 课程信息】")
    courses = Course.objects.filter(major=iot_major)
    print(f"该专业共有 {courses.count()} 门课程")
    if courses.count() > 0:
        print("  示例课程:")
        for course in courses[:10]:
            print(f"  - {course.name} ({course.code}) - {course.credits}学分")
    
    # 6. 检查课程支持关系
    print("\n【6. 课程支持关系】")
    course_supports = CourseSupport.objects.filter(course__major=iot_major)
    print(f"共有 {course_supports.count()} 条课程支持关系")
    if course_supports.count() > 0:
        print("  示例:")
        for support in course_supports[:10]:
            print(f"  - {support.course.name} -> 指标点{support.indicator.requirement.sequence}.{support.indicator.sequence} (权重: {support.weight})")
    
    # 7. 数据完整性检查
    print("\n【7. 数据完整性检查】")
    print(f"? 专业数量: {majors.count()}")
    print(f"? 培养目标数量: {objectives.count()}")
    print(f"? 毕业要求数量: {requirements.count()}")
    print(f"? 指标点数量: {IndicatorPoint.objects.filter(requirement__major=iot_major).count()}")
    print(f"? 课程数量: {courses.count()}")
    print(f"? 培养目标支持关系: {obj_supports.count()}")
    print(f"? 课程支持关系: {course_supports.count()}")
    
    # 判断数据是否完整
    if (objectives.count() > 0 and requirements.count() > 0 and 
        courses.count() > 0 and course_supports.count() > 0):
        print("\n" + "=" * 80)
        print("? 数据验证通过！物联网工程专业数据已成功导入数据库。")
        print("=" * 80)
        return True
    else:
        print("\n" + "=" * 80)
        print("??  数据不完整，可能需要重新导入。")
        print("=" * 80)
        return False

if __name__ == '__main__':
    try:
        verify_data()
    except Exception as e:
        print(f"\n? 验证过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
