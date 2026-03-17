# -*- coding: utf-8 -*-
import pandas as pd
import os
import re
from django.core.management.base import BaseCommand
from core.models import Major, Course, GraduationRequirement, IndicatorPoint, CourseSupport
from decimal import Decimal

class Command(BaseCommand):
    help = '上帝模式 V3：自动补全缺失骨架 + 强力导入'

    def add_arguments(self, parser):
        parser.add_argument('--major', type=str, required=True, help='专业名称')

    def handle(self, *args, **options):
        major_name = options['major'].strip()
        target_file = f"{major_name}.xlsx"
        
        major_obj, _ = Major.objects.get_or_create(name=major_name)
        self.stdout.write(self.style.WARNING(f"🚀 正在为 [{major_name}] 执行全量数据对齐..."))

        xlsx = pd.ExcelFile(target_file)

        # --- 1. 优先处理专业属性 (修复学制为 None 的问题) ---
        if 'major' in xlsx.sheet_names:
            df_m = pd.read_excel(xlsx, sheet_name='major', header=None)
            for _, row in df_m.iterrows():
                v = [str(c).strip() for c in row.values if pd.notna(c)]
                row_text = "".join(v).lower()
                if 'duration' in row_text or '学制' in row_text:
                    # 尝试从这一行里抓取数字或“四年”
                    major_obj.duration = v[-1] 
                    major_obj.save()
            self.stdout.write(f"✅ 专业学制已同步: {major_obj.duration}")

        # --- 2. 从 Excel 重建毕业要求骨架 ---
        if 'graduation_requirement' in xlsx.sheet_names:
            df_r = pd.read_excel(xlsx, sheet_name='graduation_requirement', header=None)
            for _, row in df_r.iterrows():
                v = [str(c).strip() for c in row.values if pd.notna(c)]
                if len(v) >= 3 and 'GraduationRequirement' in v[0]:
                    seq = "".join(re.findall(r'\d+', v[3]))
                    if seq:
                        GraduationRequirement.objects.get_or_create(
                            major=major_obj, sequence=seq, defaults={'content': v[2]}
                        )
            self.stdout.write("✅ 毕业要求骨架同步完成")

        # --- 3. 导入课程 ---
        if 'course' in xlsx.sheet_names:
            df_c = pd.read_excel(xlsx, sheet_name='course', header=None)
            for _, row in df_c.iterrows():
                v = [str(c).strip() for c in row.values if pd.notna(c)]
                if len(v) >= 5 and 'Course' in v[0] and v[1] == 'code':
                    Course.objects.update_or_create(
                        code=v[2], major=major_obj,
                        defaults={'name': v[3], 'credits': Decimal(v[4]) if v[4].replace('.','',1).isdigit() else 0}
                    )

        # --- 4. 导入支撑矩阵 (核心：缺失则自动补全) ---
        self.stdout.write("🔗 开始深度挂靠支撑关系...")
        s_count = 0
        w_map = {'H': 1.0, 'M': 0.5, 'L': 0.2}
        
        if 'course_support' in xlsx.sheet_names:
            df_s = pd.read_excel(xlsx, sheet_name='course_support', header=None)
            for _, row in df_s.iterrows():
                v = [str(c).strip() for c in row.values if pd.notna(c)]
                if 'CourseSupport' not in v[0] or len(v) < 6: continue
                
                c_name, sub_seq = v[2], v[3]
                req_num = "".join(re.findall(r'\d+', v[4]))
                w_key = v[5].upper()

                # 找课程
                course = Course.objects.filter(major=major_obj, name=c_name).first() or \
                         Course.objects.filter(major=major_obj, code=c_name).first()
                
                # 【核心逻辑：自动补全缺失的毕业要求和指标点】
                req_obj, _ = GraduationRequirement.objects.get_or_create(
                    major=major_obj, sequence=req_num, 
                    defaults={'content': f'毕业要求 {req_num} (由 Excel 自动生成)'}
                )
                
                indicator_obj, _ = IndicatorPoint.objects.get_or_create(
                    requirement=req_obj, sequence=sub_seq,
                    defaults={'content': f'指标点 {req_num}-{sub_seq} (由 Excel 自动生成)'}
                )

                if course and w_key in w_map:
                    CourseSupport.objects.update_or_create(
                        course=course, indicator=indicator_obj,
                        defaults={'weight': Decimal(str(w_map[w_key]))}
                    )
                    s_count += 1
        
        self.stdout.write(self.style.SUCCESS(f"✨ 导入圆满完成！最终支撑条数：{s_count}"))