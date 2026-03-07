# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from core.models import Course, IndicatorPoint, CourseSupport
from django.db.models import Sum

class Command(BaseCommand):
    help = '执行人才培养方案先修时序与支撑强度逻辑检测'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(">>> 正在启动物联网工程专业逻辑闭环检测...\n"))

        # 1. 先修课时序检测
        self.stdout.write("--- 1. 先修课开课时序检测 ---")
        seq_errors = 0
        courses = Course.objects.all().prefetch_related('prerequisites')
        
        for course in courses:
            if not course.semester:
                continue
            for pre in course.prerequisites.all():
                # 核心逻辑：如果先修课的开课学期晚于或等于当前课，则报错
                if pre.semester and pre.semester >= course.semester:
                    self.stdout.write(self.style.ERROR(
                        f"  [发现矛盾] 《{course.name}》(学期 {course.semester}) "
                        f"的先修课 《{pre.name}》(学期 {pre.semester}) 安排得不合理！"
                    ))
                    seq_errors += 1
        
        if seq_errors == 0:
            self.stdout.write(self.style.SUCCESS("  [通过] 所有先修课开课时序逻辑合理。"))

        # 2. 指标点支撑强度检测
        self.stdout.write("\n--- 2. 毕业要求支撑强度检测 ---")
        weight_errors = 0
        # 查找所有指标点，并计算其总支撑权重之和
        indicators = IndicatorPoint.objects.all().select_related('requirement')
        
        for ind in indicators:
            total_weight = CourseSupport.objects.filter(indicator=ind).aggregate(Sum('weight'))['weight__sum'] or 0
            # 预警逻辑：如果该指标点的总支撑权重小于 0.5 (阈值可调)
            if total_weight < 0.5:
                self.stdout.write(self.style.WARNING(
                    f"  [风险] 指标点 {ind.requirement.sequence}.{ind.sequence} 支撑权重总和为 {total_weight:.2f} (建议 > 0.5)"
                ))
                weight_errors += 1
        
        if weight_errors == 0:
            self.stdout.write(self.style.SUCCESS("  [通过] 所有指标点均有足够的课程支撑。"))
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("逻辑检测任务已完成"))