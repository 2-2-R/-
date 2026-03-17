# 后端主目录下的 urls.py
from django.contrib import admin
from django.urls import path, include # 👈 确保导入了 include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')), # 👈 新增这一行：所有 /api/ 开头的请求都交给 core 处理
]