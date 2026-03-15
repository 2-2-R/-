# -*- coding: utf-8 -*-
import pdfplumber
import re
import sys

# 强制设置输出编码为 UTF-8，防止控制台乱码
sys.stdout.reconfigure(encoding='utf-8')

def debug_pdf():
    file_path = "延安大学人才培养方案理科.pdf"
    try:
        with pdfplumber.open(file_path) as pdf:
            # 检查第 128 页（索引 127）
            # 如果你怀疑页码不对，可以循环打印 pdf.pages 找到包含“矩阵图”字样的页面
            page = pdf.pages[127] 
            table = page.extract_table()
            
            if not table:
                print("Error: No table found on page 128. Please check the physical page number.")
                return

            print("Table found! Scanning content...\n")
            
            # 1. 打印表头前几个单元格
            header = [str(c).replace('\n', '') for c in table[0] if c]
            print("--- [Header Preview] ---")
            print(header[:15]) 
            
            # 2. 检查是否有类似 1-1 的编号
            nums_found = re.findall(r'\d+', "".join(header))
            print("\n--- [Indicator Detection] ---")
            print(f"Numbers found in header: {nums_found[:20]}")

            # 3. 打印前 10 行课程名称（看看是不是我们要的那个表）
            print("\n--- [Course Name Preview] ---")
            for i, row in enumerate(table[1:11]):
                if row and row[0]:
                    print(f"Row {i+1} first cell: {str(row[0]).replace('\n', '')}")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    debug_pdf()