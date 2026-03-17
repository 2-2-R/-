import os
import re
import uuid
from django.core.management.base import BaseCommand
from core.models import Major, GraduationRequirement, IndicatorPoint, TrainingObjective

class Command(BaseCommand):
    help = 'V4 Script - Fix Database Unique Code Error'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='scheme.txt')

    def handle(self, *args, **options):
        file_path = options['file']
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        content = re.sub(r'\[.*?\]', '', content)
        lines = content.split('\n')
        current_major = None
        section = None

        self.stdout.write(self.style.WARNING("Starting parser..."))

        for line in lines:
            clean_line = line.strip()
            if not clean_line: continue

            if '\u4e13\u4e1a\u672c\u79d1\u4eba\u624d\u57f9\u517b\u65b9\u6848' in clean_line:
                major_name = clean_line.split('\u4e13\u4e1a')[0].strip() 
                major_name = re.sub(r'\(.*?\)', '', major_name).strip()
                
                # ? 核心修复：生成一个随机且唯一的代号喂给数据库
                unique_code = uuid.uuid4().hex[:6].upper()
                current_major, _ = Major.objects.get_or_create(
                    name=major_name, 
                    defaults={'code': unique_code}
                )
                
                self.stdout.write(self.style.SUCCESS(f"Found Major: {major_name}"))
                section = None
                continue

            if not current_major: continue

            if '\u4e00\u3001\u57f9\u517b\u76ee\u6807' in clean_line: section = "OBJ"; continue
            if '\u4e8c\u3001\u6bd5\u4e1a\u8981\u6c42' in clean_line: section = "REQ"; continue
            if '\u4e94\u3001\u5b66\u5236\u4e0e\u5b66\u4f4d' in clean_line: section = "INFO"; continue

            if section == "OBJ":
                obj_match = re.match(r'^(\u76ee\u6807\s*(\d+)|(\d+)\.)\s*(.*)', clean_line)
                if obj_match:
                    seq = obj_match.group(2) or obj_match.group(3)
                    text = obj_match.group(4).strip()
                    TrainingObjective.objects.update_or_create(major=current_major, sequence=seq, defaults={'content': text})

            elif section == "REQ":
                req_header = re.match(r'^(\d+)\.\s*(.*?)[:\uff1a](.*)', clean_line)
                if req_header:
                    seq, title, text = req_header.groups()
                    current_req, _ = GraduationRequirement.objects.update_or_create(major=current_major, sequence=seq, defaults={'content': f"{title.strip()}: {text.strip()}"})
                
                ip_match = re.search(r'(\d+)-(\d+)\s*(.*)', clean_line)
                if ip_match:
                    m_seq, s_seq, text = ip_match.groups()
                    parent_req, _ = GraduationRequirement.objects.get_or_create(major=current_major, sequence=m_seq)
                    IndicatorPoint.objects.update_or_create(requirement=parent_req, sequence=s_seq, defaults={'content': text.strip()})

            elif section == "INFO" and '\u5b66\u5236' in clean_line:
                dur_match = re.search(r'\u5b66\u5236(.*?)\u5e74', clean_line)
                if dur_match:
                    current_major.duration = dur_match.group(1).strip()
                    current_major.save()

        self.stdout.write(self.style.SUCCESS("Import completed successfully!"))