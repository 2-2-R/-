from .signals import _thread_locals

class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 将当前请求的用户存入线程变量
        _thread_locals.user = request.user if request.user.is_authenticated else None
        response = self.get_response(request)
        # 请求结束后清理，防止内存泄漏
        if hasattr(_thread_locals, 'user'):
            del _thread_locals.user
        return response