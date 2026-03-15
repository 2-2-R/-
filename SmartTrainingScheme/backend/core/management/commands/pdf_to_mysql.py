# -*- coding: utf-8 -*-
import pdfplumber, re
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Major, Course
from decimal import Decimal

class Command(BaseCommand):
    help = '使用 update_or_create 解决重复课程编码冲突问题'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='延安大学人才培养方案理科.pdf')
        parser.add_argument('--start', type=int, required=True)
        parser.add_argument('--end', type=int, required=True)
        parser.add_argument('--major', type=str, default='物联网工程')

    def handle(self, *args, **options):
        # 匹配延安大学课程编码正则
        code_pattern = re.compile(r'^[0-9A-Z]{6,12}$')

        with pdfplumber.open(options['file']) as pdf:
            with transaction.atomic():
                major_obj, _ = Major.objects.get_or_create(name=options['major'])
                
                # 注意：如果使用 update_or_create，可以不删旧数据，或者按需保留
                # Course.objects.filter(major=major_obj).delete() 

                count = 0
                for i in range(options['start']-1, options['end']):
                    table = pdf.pages[i].extract_table()
                    if not table: continue

                    for row in table:
                        clean_row = [str(cell).replace('\n', '').strip() if cell else "" for cell in row]
                        
                        # 针对物联网工程表的索引 (3:编码, 4:名称, 5:学分)
                        if len(clean_row) >= 6:
                            code = clean_row[3]
                            name = clean_row[4]
                            
                            if code_pattern.match(code):
                                try:
                                    credits_val = Decimal(clean_row[5])
                                except:
                                    credits_val = Decimal('0')

                                # --- 核心修改：使用 update_or_create 避免唯一键冲突 ---
                                course_obj, created = Course.objects.update_or_create(
                                    code=code,  # 以 code 作为查找唯一标识
                                    defaults={
                                        'major': major_obj,
                                        'name': name,
                                        'credits': credits_val
                                    }
                                )
                                if created:
                                    count += 1
                
                self.stdout.write(self.style.SUCCESS(f"成功处理课程。新增: {count} 门，其余已自动更新。"))