# -*- coding: utf-8 -*-
import pandas as pd
import re
import os
from django.core.management.base import BaseCommand
from core.models import Major, Course, IndicatorPoint, CourseSupport
from decimal import Decimal

class Command(BaseCommand):
    help = '全能导入脚本：支持 .xlsx 和 .csv，适配数计学院表格布局'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, required=True, help='文件路径 (.xlsx 或 .csv)')
        parser.add_argument('--major', type=str, required=True, help='专业名称')

    def handle(self, *args, **options):
        file_path = options['file']
        major_name = options['major']

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"找不到文件: {file_path}"))
            return

        # 1. 根据后缀名选择读取方式
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == '.xlsx':
                # 如果是 Excel，跳过前 4 行说明，第 5 行是表头
                df = pd.read_excel(file_path, skiprows=4)
            else:
                # 如果是 CSV，尝试 UTF-8 或 GBK 编码，同样跳过前 4 行
                try:
                    df = pd.read_csv(file_path, skiprows=4, encoding='utf-8')
                except UnicodeDecodeError:
                    df = pd.read_csv(file_path, skiprows=4, encoding='gbk')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"文件读取失败: {e}"))
            return

        # 2. 获取或创建专业 (增加默认 code 避免之前的 Duplicate entry 错误)
        major_obj, _ = Major.objects.get_or_create(
            name=major_name,
            defaults={'code': 'AUTO_' + major_name}
        )

        # 3. 预加载指标点 (1-1, 1.1 等映射)
        indicators = IndicatorPoint.objects.filter(requirement__major=major_obj)
        ind_map = {f"{i.requirement.sequence}-{i.sequence}": i for i in indicators}
        ind_map.update({f"{i.requirement.sequence}.{i.sequence}": i for i in indicators})

        weight_map = {'H': 1.0, 'M': 0.5, 'L': 0.2, '●': 1.0, '◎': 0.5, '○': 0.2}
        
        # 4. 清洗 DataFrame
        # 你的表格通常第一列是序号或空列，我们直接通过列名访问
        df.columns = [str(c).strip() for c in df.columns]
        
        course_count = 0
        support_count = 0

        # 清理该专业旧课程，准备重新灌库
        Course.objects.filter(major=major_obj).delete()

        for _, row in df.iterrows():
            # 兼容处理：获取课程编号和名称
            # 你的 CSV 结构中，列名通常是 '课程编号' 和 '课程名称'
            code = str(row.get('课程编号', '')).strip()
            name = str(row.get('课程名称', '')).strip()

            if not code or code == 'nan' or 'Unnamed' in code:
                continue

            try:
                credits_val = Decimal(str(row.get('学分', '0')))
            except:
                credits_val = Decimal('0')

            # 创建课程
            course_obj = Course.objects.create(
                code=code, major=major_obj, name=name, credits=credits_val
            )
            course_count += 1

            # 5. 扫描列名中包含的支撑强度 (1-1, 2-1 等)
            for col in df.columns:
                val = str(row.get(col, '')).strip().upper()
                if val in weight_map:
                    match = re.search(r'(\d+)[-\.](\d+)', col)
                    if match:
                        key = f"{match.group(1)}-{match.group(2)}"
                        if key in ind_map:
                            CourseSupport.objects.create(
                                course=course_obj,
                                indicator=ind_map[key],
                                weight=Decimal(str(weight_map[val]))
                            )
                            support_count += 1

        self.stdout.write(self.style.SUCCESS(f"【{major_name}】导入成功！课程: {course_count}，支撑关系: {support_count}"))