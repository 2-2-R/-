# -*- coding: utf-8 -*-
import pdfplumber, re
from django.core.management.base import BaseCommand
from core.models import Major, Course, IndicatorPoint, CourseSupport
from decimal import Decimal

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='延安大学人才培养方案理科.pdf')
        parser.add_argument('--start', type=int, required=True)
        parser.add_argument('--end', type=int, required=True)
        parser.add_argument('--major', type=str, default='物联网工程')

    def handle(self, *args, **options):
        weight_map = {'H': 1.0, 'M': 0.5, 'L': 0.2, '●': 1.0, '◎': 0.5, '○': 0.2}
        
        with pdfplumber.open(options['file']) as pdf:
            major_obj = Major.objects.get(name=options['major'])
            # 建立 (毕业要求序号, 指标点序号) -> 对象 的映射
            inds = IndicatorPoint.objects.filter(requirement__major=major_obj)
            ind_dict = {(i.requirement.sequence, i.sequence): i for i in inds}

            count = 0
            for i in range(options['start']-1, options['end']):
                table = pdf.pages[i].extract_table()
                if not table: continue
                
                # 1. 寻找表头（只要包含数字的列都视为指标点候选列）
                header_map = {} # col_idx -> IndicatorPoint 对象
                for idx, cell in enumerate(table[0]):
                    nums = re.findall(r'\d+', str(cell))
                    if len(nums) >= 2: # 发现类似 1-1 的数字对
                        key = (int(nums[0]), int(nums[1]))
                        if key in ind_dict:
                            header_map[idx] = ind_dict[key]
                
                # 2. 扫描数据行
                for row in table[1:]:
                    if not row or not row[0]: continue
                    
                    # 课程名模糊清洗：只保留汉字，防止序号和括号干扰匹配
                    c_name_raw = str(row[0]).replace('\n', '')
                    c_name_clean = "".join(re.findall(r'[\u4e00-\u9fa5]+', c_name_raw))
                    
                    # 在数据库中查找（匹配前3个汉字）
                    course = Course.objects.filter(major=major_obj, name__icontains=c_name_clean[:3]).first()
                    
                    if course:
                        for col_idx, cell in enumerate(row):
                            val = str(cell).strip().upper()
                            if val in weight_map and col_idx in header_map:
                                CourseSupport.objects.update_or_create(
                                    course=course, indicator=header_map[col_idx],
                                    defaults={'weight': Decimal(str(weight_map[val]))}
                                )
                                count += 1

            self.stdout.write(self.style.SUCCESS(f"矩阵解析完成！建立支撑关系: {count}条"))