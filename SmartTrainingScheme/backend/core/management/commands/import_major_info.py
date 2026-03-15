# -*- coding: utf-8 -*-
import pdfplumber
import re
from django.core.management.base import BaseCommand
from core.models import Major, TrainingObjective, GraduationRequirement, IndicatorPoint

class Command(BaseCommand):
    help = '从 PDF 提取专业所有文本信息并灌入 MySQL'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='延安大学人才培养方案理科.pdf')
        parser.add_argument('--start', type=int, required=True)
        parser.add_argument('--end', type=int, required=True)
        parser.add_argument('--major', type=str, default='物联网工程')

    def handle(self, *args, **options):
        major_name = options['major']
        with pdfplumber.open(options['file']) as pdf:
            text = ""
            for i in range(options['start']-1, options['end']):
                text += pdf.pages[i].extract_text() + "\n"

            # 使用关键词切割文本块
            sections = {
                "duration": self.extract_section(text, "学制与学位", "主干学科"),
                "disciplines": self.extract_section(text, "主干学科", "主干课程"),
                "core_courses": self.extract_section(text, "主干课程", "主要实践性教学环节"),
                "grad_cond": self.extract_section(text, "毕业条件", "学士学位授予条件"),
                "degree_cond": self.extract_section(text, "学士学位授予条件", "课程设置")
            }

            major_obj, _ = Major.objects.get_or_create(name=major_name)
            major_obj.duration = sections["duration"]
            major_obj.core_disciplines = sections["disciplines"]
            major_obj.core_courses = sections["core_courses"]
            major_obj.graduation_condition = sections["grad_cond"]
            major_obj.degree_condition = sections["degree_cond"]
            major_obj.save()

            self.stdout.write(self.style.SUCCESS(f"成功更新 {major_name} 的所有文本描述信息。"))

    def extract_section(self, text, start_key, end_key):
        pattern = f"{start_key}(.*?){end_key}"
        match = re.search(pattern, text, re.S)
        return match.group(1).strip() if match else "未找到"