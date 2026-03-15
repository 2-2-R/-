# -*- coding: utf-8 -*-
import pdfplumber, re
from django.core.management.base import BaseCommand
from core.models import Major, GraduationRequirement, IndicatorPoint
from decimal import Decimal

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='延安大学人才培养方案—数计学院.pdf')
        parser.add_argument('--start', type=int, required=True)
        parser.add_argument('--end', type=int, required=True)
        parser.add_argument('--major', type=str, default='物联网工程')

    def handle(self, *args, **options):
        with pdfplumber.open(options['file']) as pdf:
            text = "\n".join([p.extract_text() for p in pdf.pages[options['start']-1 : options['end']]])
            # 强力清洗：去掉所有奇怪的空白字符
            text = re.sub(r'[ \t]+', ' ', text)
            
            # 使用 defaults 确保在创建新专业时，自动生成一个 code
            major_obj, _ = Major.objects.get_or_create(
                name=options['major'],
                defaults={'code': 'AUTO_' + options['major']}
            )
            GraduationRequirement.objects.filter(major=major_obj).delete()

            # 匹配所有 1. XXX 格式的毕业要求
            req_matches = list(re.finditer(r'(?P<seq>\d+)[\.、\s]+(?P<content>[\u4e00-\u9fa5]{2,10})', text))
            
            for i, match in enumerate(req_matches):
                req = GraduationRequirement.objects.create(
                    major=major_obj, sequence=int(match.group('seq')), content=match.group('content').strip()
                )
                # 确定当前指标点的扫描范围
                start, end = match.end(), req_matches[i+1].start() if i+1 < len(req_matches) else len(text)
                sub_text = text[start:end]
                
                # 暴力抓取所有形如 1-1, 1.1, 1- 1 的数字对
                inds = re.findall(r'(\d+)\s*[-\. ]\s*(\d+)[\.、\s]+(.*?)(?=\d+\s*[-\. ]\s*\d+|$)', sub_text, re.S)
                for ind in inds:
                    IndicatorPoint.objects.create(
                        requirement=req, sequence=int(ind[1]), 
                        content=ind[2].strip().replace('\n', ''), weight=Decimal('0.0')
                    )
        self.stdout.write(self.style.SUCCESS(f"文本框架修复完成。"))