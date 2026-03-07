# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os
import sys

def main():
    """Run administrative tasks."""
    # 确保这里指向你之前找到的 config 文件夹
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()