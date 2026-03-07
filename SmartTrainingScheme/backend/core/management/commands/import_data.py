# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import (
    Major, 
    GraduationRequirement, 
    IndicatorPoint, 
    Course,
    CourseSupport
)
from decimal import Decimal

class Command(BaseCommand):
    help = '物联网工程专业数据智能导入工具：适配 8 列混合超级表格'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Excel 文件的路径')
        parser.add_argument('--clear', action='store_true', help='是否在导入前清空数据')

    def handle(self, *args, **options):
        file_path = options['file']
        
        # 统计计数器，用于去重统计
        self.stats = {
            'major': set(),
            'requirement': set(),
            'indicator': set(),
            'course': set(),
            'matrix': 0
        }
        self.current_course = None  # 用于追踪当前正在处理的课程对象
        
        if not file_path or not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'找不到文件: {file_path}'))
            return

        if options['clear']:
            self.stdout.write(self.style.WARNING("正在清空数据库原有数据..."))
            CourseSupport.objects.all().delete()
            IndicatorPoint.objects.all().delete()
            GraduationRequirement.objects.all().delete()
            Course.objects.all().delete()
            Major.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(f'开始解析混合格式数据: {file_path}'))

        try:
            excel_data = pd.ExcelFile(file_path)
            
            with transaction.atomic():
                # 遍历所有标签页
                for sheet in excel_data.sheet_names:
                    # 使用 header=None 以便手动处理每一行，增加容错性
                    df = pd.read_excel(excel_data, sheet_name=sheet, header=None)
                    self._parse_mixed_data(df)

            self.print_summary()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'严重错误: {str(e)}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

    def _convert_weight(self, val):
        """将 H/M/L 定性评价智能转换为 OBE 支撑分值"""
        if pd.isna(val) or val == '': return Decimal('0.1')
        s = str(val).strip().upper()
        mapping = {'H': Decimal('0.5'), 'M': Decimal('0.3'), 'L': Decimal('0.1')}
        return mapping.get(s, Decimal('0.1'))

    def _parse_mixed_data(self, df):
        """处理 8 列混合垂直数据"""
        major_obj = None
        
        for index, row in df.iterrows():
            try:
                model = str(row[0]).strip()
                field = str(row[1]).strip()
                val = str(row[2]).strip()
            except:
                continue
            
            # 跳过空行及标题行
            if model in ['模型', 'nan'] or val == 'nan' or not model:
                continue

            # 1. 识别专业信息
            if model == 'Major':
                if field == 'name':
                    major_obj, _ = Major.objects.get_or_create(name=val, defaults={'code': '080905'})
                    self.stats['major'].add(val)

            # 2. 识别毕业要求
            elif model == 'GraduationRequirement':
                m = major_obj or Major.objects.first()
                if field == 'sequence' and m:
                    try:
                        seq = int(float(val))
                        GraduationRequirement.objects.get_or_create(major=m, sequence=seq)
                        self.stats['requirement'].add(f"{m.id}_{seq}")
                    except: pass

            # 3. 识别课程与支撑关系 (基于 8 列布局)
            elif model == 'Course':
                m = major_obj or Major.objects.first()
                if not m: continue
                
                # 如果是代码行，创建或定位课程
                if field == 'code' or field == '课程代码':
                    course_code = val
                    course_name = str(row[3]).strip() if len(row) > 3 else "未知课程"
                    
                    self.current_course, _ = Course.objects.update_or_create(
                        code=course_code, major=m,
                        defaults={
                            'name': course_name,
                            'credits': Decimal('0') # 核心修复：初始默认值为0，防止非空约束报错
                        }
                    )
                    self.stats['course'].add(course_code)
                
                # 如果当前存在已定位的课程对象，则更新其属性
                if self.current_course:
                    # 只有当字段是学分或名称时才更新对应字段
                    if field in ['credits', '学分']:
                        self.current_course.credits = Decimal(val)
                    elif field in ['name', '课程名称']:
                        self.current_course.name = val

                    # 每一行都尝试提取扩展属性 (第 5 列：类别，第 6 列：学期)
                    try:
                        if len(row) > 4 and pd.notna(row[4]): 
                            self.current_course.category = str(row[4]).strip()
                        if len(row) > 5 and pd.notna(row[5]): 
                            self.current_course.semester = int(float(row[5]))
                    except: pass
                    
                    self.current_course.save()

                    # 提取支撑关系 (第 7 列：关联要求序号，第 8 列：程度)
                    if len(row) > 7:
                        req_val = row[6]
                        level_val = row[7]
                        if pd.notna(req_val) and pd.notna(level_val):
                            self._link_matrix(self.current_course, req_val, level_val)

    def _link_matrix(self, course, req_val, level_val):
        """建立支撑关联并自动补全指标点"""
        try:
            req_str = str(req_val)
            r_seq = int(float(req_str.split('.')[0])) if '.' in req_str else int(float(req_str))
            i_seq = int(float(req_str.split('.')[1])) if '.' in req_str else 1
            
            req = GraduationRequirement.objects.filter(major=course.major, sequence=r_seq).first()
            if req:
                indicator, i_created = IndicatorPoint.objects.get_or_create(
                    requirement=req, sequence=i_seq,
                    defaults={'content': f'指标点 {r_seq}.{i_seq}', 'weight': Decimal('0.2')}
                )
                if i_created: self.stats['indicator'].add(f"{req.id}_{i_seq}")
                
                CourseSupport.objects.update_or_create(
                    course=course, indicator=indicator,
                    defaults={'weight': self._convert_weight(level_val)}
                )
                self.stats['matrix'] += 1
        except:
            pass

    def print_summary(self):
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("数据导入任务总结"))
        self.stdout.write(f"1. 专业信息: {len(self.stats['major'])} 条")
        self.stdout.write(f"2. 毕业要求: {len(self.stats['requirement'])} 条")
        self.stdout.write(f"3. 自动生成指标点: {len(self.stats['indicator'])} 个")
        self.stdout.write(f"4. 导入课程: {len(self.stats['course'])} 门")
        self.stdout.write(f"5. 支撑矩阵链接: {self.stats['matrix']} 条")
        self.stdout.write("="*50 + "\n")