# -*- coding: utf-8 -*-
import os
import re
from django.core.management.base import BaseCommand
from core.models import Major, GraduationRequirement, IndicatorPoint, TrainingObjective

class Command(BaseCommand):
    help = '全自动解析 scheme.txt 构建全院 6 个专业骨架'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='scheme.txt', help='文本文件路径')

    def handle(self, *args, **options):
        file_path = options['file']
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"❌ 找不到文件: {file_path}"))
            return

        content = ""
        for enc in ['utf-8', 'gbk', 'utf-8-sig']:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue

        lines = content.split('\n')
        current_major = None
        section = None 

        self.stdout.write(self.style.WARNING("🚀 正在深度解析培养方案文本..."))

        for line in lines:
            line = line.strip()
            if not line: continue

            # 注意这行！已经没有反斜杠结尾的语法错误了
            clean_line = re.sub(r'\', '', line).strip()
            if not clean_line: continue

            if '专业本科人才培养方案' in clean_line:
                major_name = clean_line.split('专业')[0].strip()
                major_name = re.sub(r'\(.*?\)', '', major_name).strip()
                current_major, _ = Major.objects.get_or_create(name=major_name)
                self.stdout.write(self.style.SUCCESS(f"\n📍 发现专业: {major_name}"))
                section = None
                continue

            if not current_major: continue

            if "一、培养目标" in clean_line: section = "OBJ"; continue
            if "二、毕业要求" in clean_line: section = "REQ"; continue
            if "五、学制与学位" in clean_line: section = "INFO"; continue

            if section == "OBJ":
                obj_match = re.match(r'^(目标\s*(\d+)|(\d+)\.)\s*(.*)', clean_line)
                if obj_match:
                    seq = obj_match.group(2) or obj_match.group(3)
                    text = obj_match.group(4).strip()
                    TrainingObjective.objects.update_or_create(
                        major=current_major, sequence=seq, defaults={'content': text}
                    )

            elif section == "REQ":
                req_header = re.match(r'^(\d+)\.\s*(.*?)[：:](.*)', clean_line)
                if req_header:
                    seq, title, text = req_header.groups()
                    current_req, _ = GraduationRequirement.objects.update_or_create(
                        major=current_major, sequence=seq, 
                        defaults={'content': f"{title.strip()}: {text.strip()}"}
                    )
                
                ip_match = re.search(r'(\d+)-(\d+)\s*(.*)', clean_line)
                if ip_match:
                    m_seq, s_seq, text = ip_match.groups()
                    parent_req, _ = GraduationRequirement.objects.get_or_create(
                        major=current_major, sequence=m_seq
                    )
                    IndicatorPoint.objects.update_or_create(
                        requirement=parent_req, sequence=s_seq, defaults={'content': text.strip()}
                    )

            elif section == "INFO" and "学制" in clean_line:
                dur_match = re.search(r'学制(.*?)年', clean_line)
                if dur_match:
                    current_major.duration = dur_match.group(1).strip()
                    current_major.save()

        self.stdout.write(self.style.SUCCESS("\n✨ 数据骨架重建完成！"))