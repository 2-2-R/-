# -*- coding: utf-8 -*-
import os
import re
import pandas as pd
from django.core.management.base import BaseCommand
from core.models import Major, IndicatorPoint

class Command(BaseCommand):
    help = '将旧版格式的 Excel 转换为 django-import-export 标准导入模板'

    def handle(self, *args, **options):
        # 1. 致命错误拦截：检查数据库是否为空
        ip_count = IndicatorPoint.objects.count()
        if ip_count == 0:
            self.stdout.write(self.style.ERROR("\n❌ 致命错误：你的数据库里没有任何【指标点】数据！"))
            self.stdout.write(self.style.WARNING("👉 必须先成功执行: python manage.py import_all_text --file scheme.txt\n"))
            return

        majors = [
            '计算机科学与技术', '软件工程', '数据科学与大数据技术', 
            '数学与应用数学', '物联网工程', '信息与计算科学'
        ]
        
        all_courses = []
        all_supports = []
        w_map = {'H': 1.0, 'M': 0.5, 'L': 0.2}

        self.stdout.write(self.style.WARNING("🚀 启动自动化格式转换向导..."))

        for major_name in majors:
            file_path = f"{major_name}.xlsx"
            if not os.path.exists(file_path):
                continue
                
            self.stdout.write(f"🔄 正在提取 [{major_name}] 的数据...")
            
            try:
                xlsx = pd.ExcelFile(file_path)
            except Exception:
                continue
                
            course_map = {} 
            
            # --- 1. 提取课程 ---
            for sheet in xlsx.sheet_names:
                df = pd.read_excel(xlsx, sheet_name=sheet, header=None)
                for _, row in df.iterrows():
                    v = [str(c).strip() for c in row.values if pd.notna(c)]
                    if len(v) >= 4 and 'Course' in v[0] and v[1] == 'code':
                        code, name = v[2], v[3]
                        cred = v[4] if len(v) > 4 else '0'
                        cred_val = cred if cred.replace('.', '', 1).isdigit() else '0'
                        
                        all_courses.append({'code': code, 'name': name, 'credits': cred_val, '专业': major_name})
                        course_map[name] = code
                        course_map[code] = code
            
            # --- 2. 提取支撑矩阵 ---
            miss_indicator_count = 0
            for sheet in xlsx.sheet_names:
                df = pd.read_excel(xlsx, sheet_name=sheet, header=None)
                for _, row in df.iterrows():
                    v = [str(c).strip() for c in row.values if pd.notna(c)]
                    # 放宽条件：只要行首是 CourseSupport 就抓，不管有几列
                    if len(v) >= 4 and 'CourseSupport' in v[0]:
                        c_name = v[2]
                        course_code = course_map.get(c_name)
                        if not course_code: continue

                        # 把后面的单元格全拼起来找数字
                        row_text = " ".join(v[3:]) 
                        nums = re.findall(r'\d+', row_text)
                        
                        if not nums: continue
                            
                        if len(nums) >= 2:
                            req_num, sub_seq = nums[0], nums[1]
                        else:
                            req_num, sub_seq = nums[0], "1"
                            
                        # 找权重 (H/M/L)
                        w_key = "H" # 默认给个 H
                        for char in v:
                            if char.upper() in w_map:
                                w_key = char.upper()
                                break
                            
                        # 去数据库查询指标点
                        indicator = IndicatorPoint.objects.filter(
                            requirement__major__name=major_name,
                            requirement__sequence=req_num,
                            sequence=sub_seq
                        ).first() or IndicatorPoint.objects.filter(
                            requirement__major__name=major_name,
                            requirement__sequence=req_num
                        ).first()

                        if indicator:
                            all_supports.append({
                                '课程代码': course_code,
                                '指标点ID': indicator.id,
                                'weight': w_map[w_key]
                            })
                        else:
                            miss_indicator_count += 1
            
            if miss_indicator_count > 0:
                self.stdout.write(self.style.WARNING(f"  ⚠️ 警告: [{major_name}] 有 {miss_indicator_count} 条关系因为在数据库找不到指标点而跳过。"))

        # --- 3. 导出模板 ---
        if all_courses:
            pd.DataFrame(all_courses).to_excel('标准导入模板_课程.xlsx', index=False)
            self.stdout.write(self.style.SUCCESS(f"✅ 成功生成 [标准导入模板_课程.xlsx] (共 {len(all_courses)} 门课)"))
            
        if all_supports:
            pd.DataFrame(all_supports).to_excel('标准导入模板_支撑矩阵.xlsx', index=False)
            self.stdout.write(self.style.SUCCESS(f"✅ 成功生成 [标准导入模板_支撑矩阵.xlsx] (共 {len(all_supports)} 条连线)"))
        else:
            self.stdout.write(self.style.ERROR("❌ 支撑矩阵仍为 0。请查看上面的警告信息。"))

        self.stdout.write(self.style.SUCCESS("🎉 转换结束！"))