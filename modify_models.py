# -*- coding: utf-8 -*-
import os

file_path = 'SmartTrainingScheme/backend/core/models.py'
# We will insert the category field.
# Note: The file might have different encoding or the previous read was just displaying ? for some reason.
# We will try to match the line structure.

new_line = '    category = models.CharField(max_length=50, blank=True, null=True, verbose_name="课程性质")\n'

# Try reading as utf-8 first
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
except UnicodeDecodeError:
    # Fallback to gbk if utf-8 fails, though the file header says utf-8
    with open(file_path, 'r', encoding='gbk') as f:
        lines = f.readlines()

new_lines = []
inserted = False
for line in lines:
    if 'code = models.CharField' in line and 'unique=True' in line and not inserted:
        new_lines.append(line)
        # Preserve indentation of the previous line
        indentation = line[:line.find('code')]
        new_lines.append(indentation + 'category = models.CharField(max_length=50, blank=True, null=True, verbose_name="课程性质")\n')
        inserted = True
    else:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

if inserted:
    print("Successfully inserted 'category' field.")
else:
    print("Failed to find insertion point.")
