from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # ? 关键：当 Django 准备好时，立刻导入信号逻辑
        import core.signals