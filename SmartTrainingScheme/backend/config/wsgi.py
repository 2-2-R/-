# Django wsgi placeholder
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 必须有这一行，且变量名必须叫 application
application = get_wsgi_application()