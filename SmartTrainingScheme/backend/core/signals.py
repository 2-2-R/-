import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Course, CourseSupport, AuditLog
from threading import local

# 创建一个全局线程变量来存储当前请求的用户
_thread_locals = local()

@receiver(post_save, sender=Course)
@receiver(post_save, sender=CourseSupport)
def log_save(sender, instance, created, **kwargs):
    # 1. 获取当前登录用户（这需要配合下一步的中间件）
    user = getattr(_thread_locals, 'user', None)
    
    # 2. 判断是“新增”还是“修改”
    action = "CREATE" if created else "UPDATE"
    
    # 3. 计算当前版本号
    prev_version = AuditLog.objects.filter(
        model_name=sender.__name__, 
        object_id=str(instance.id)
    ).count()
    
    # 4. 记录日志
    AuditLog.objects.create(
        user=user,
        model_name=sender.__name__,
        action=action,
        object_id=str(instance.id),
        object_repr=str(instance),
        version=prev_version + 1
    )