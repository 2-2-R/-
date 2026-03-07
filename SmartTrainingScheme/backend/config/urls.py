from django.contrib import admin
from django.urls import path, include # 增加 include

urlpatterns = [
    path('admin/', admin.site.urls),
    # 将 api 开头的请求全部转发给 api 文件夹下的 urls.py 处理
    path('api/', include('api.urls')), 
]