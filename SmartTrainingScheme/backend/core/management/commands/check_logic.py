# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from core.models import (
    Major, TrainingObjective, GraduationRequirement, 
    IndicatorPoint, Course, CourseSupport
)
from django.db.models import Sum

class Command(BaseCommand):
    help = '综合检测数据库数据完整性、文本属性及业务逻辑闭环'

    # 注意：这里没有任何 add_arguments 方法，确保不需要任何命令行参数

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(">>> 正在启动物联网工程专业全方位数据审计...\n"))

        # --- 1. 基础数据量统计 ---
        self.stdout.write("--- 1. 基础数据量统计 ---")
        self.stdout.write(f" 专业总数: {Major.objects.count()}")
        self.stdout.write(f" 培养目标数: {TrainingObjective.objects.count()}")
        self.stdout.write(f" 毕业要求数: {GraduationRequirement.objects.count()}")
        self.stdout.write(f" 指标点总数: {IndicatorPoint.objects.count()}")
        self.stdout.write(f" 课程总数: {Course.objects.count()}")
        self.stdout.write(f" 支撑矩阵条数: {CourseSupport.objects.count()}")

        # --- 2. 核心文本属性检测 ---
        target_name = "物联网工程"
        major = Major.objects.filter(name__contains=target_name).first()
        
        if major:
            self.stdout.write(self.style.SUCCESS(f"\n--- 2. 专业文本属性审计: {major.name} ---"))
            self.stdout.write(f" [学制]: {major.duration if major.duration else '未找到'}")
            self.stdout.write(f" [学位]: {major.degree if major.degree else '未找到'}")
            self.stdout.write(f" [主干学科]: {major.core_disciplines[:40] if major.core_disciplines else '未找到'}...")
            self.stdout.write(f" [毕业条件]: {major.graduation_condition[:40] if major.graduation_condition else '未找到'}...")
            self.stdout.write(f" [学位授予条件]: {major.degree_condition[:40] if major.degree_condition else '未找到'}...")
        else:
            self.stdout.write(self.style.WARNING(f"\n[预警] 数据库中未发现名称包含 '{target_name}' 的专业。"))

        # --- 3. 业务逻辑：先修课开课时序检测 ---
        self.stdout.write("\n--- 3. 业务逻辑：先修课开课时序检测 ---")
        seq_errors = 0
        courses = Course.objects.all().prefetch_related('prerequisites')
        
        for course in courses:
            if not course.semester:
                continue
            for pre in course.prerequisites.all():
                if pre.semester and pre.semester >= course.semester:
                    self.stdout.write(self.style.ERROR(
                        f"  [发现冲突] 《{course.name}》(学期 {course.semester}) "
                        f"的先修课 《{pre.name}》(学期 {pre.semester}) 安排得不合理！"
                    ))
                    seq_errors += 1
        
        if seq_errors == 0:
            self.stdout.write(self.style.SUCCESS("  [通过] 所有先修课开课时序逻辑合理。"))
        else:
            self.stdout.write(self.style.ERROR(f"  [失败] 共发现 {seq_errors} 处时序冲突。"))

        # --- 4. 毕业要求支撑强度检测 ---
        self.stdout.write("\n--- 4. 毕业要求支撑强度检测 ---")
        weight_errors = 0
        indicators = IndicatorPoint.objects.all().select_related('requirement')
        
        for ind in indicators:
            total_weight = CourseSupport.objects.filter(indicator=ind).aggregate(Sum('weight'))['weight__sum'] or 0
            if total_weight < 0.5:
                self.stdout.write(self.style.WARNING(
                    f"  [风险] 指标点 {ind.requirement.sequence}.{ind.sequence} 支撑总权重为 {total_weight:.2f} (建议 > 0.5)"
                ))
                weight_errors += 1
        
        if weight_errors == 0:
            self.stdout.write(self.style.SUCCESS("  [通过] 所有指标点均有足够的课程支撑。"))

        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS(">>> 综合审计任务已完成！"))