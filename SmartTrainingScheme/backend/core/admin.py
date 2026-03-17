from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from .models import Major, Course, GraduationRequirement, IndicatorPoint, CourseSupport
from .models import AuditLog

# ==========================================
# 1. Resource Classes (100% ASCII Safe)
# ==========================================

class CourseResource(resources.ModelResource):
    major = fields.Field(
        column_name='\u4e13\u4e1a',  # '专业'
        attribute='major',
        widget=ForeignKeyWidget(Major, 'name')
    )

    class Meta:
        model = Course
        fields = ('code', 'name', 'credits', 'major')
        import_id_fields = ('code',)

class IndicatorPointResource(resources.ModelResource):
    requirement = fields.Field(
        column_name='\u6bd5\u4e1a\u8981\u6c42',  # '毕业要求'
        attribute='requirement',
        widget=ForeignKeyWidget(GraduationRequirement, 'sequence')
    )
    
    class Meta:
        model = IndicatorPoint
        fields = ('id', 'requirement', 'sequence', 'content')

class CourseSupportResource(resources.ModelResource):
    course = fields.Field(
        column_name='\u8bfe\u7a0b\u4ee3\u7801',  # '课程代码'
        attribute='course',
        widget=ForeignKeyWidget(Course, 'code')
    )
    indicator = fields.Field(
        column_name='\u6307\u6807\u70b9ID',  # '指标点ID'
        attribute='indicator',
        widget=ForeignKeyWidget(IndicatorPoint, 'id')
    )

    class Meta:
        model = CourseSupport
        fields = ('id', 'course', 'indicator', 'weight')

# ==========================================
# 2. Admin Registration
# ==========================================

@admin.register(Major)
class MajorAdmin(ImportExportModelAdmin):
    list_display = ('name', 'duration', 'degree')

@admin.register(GraduationRequirement)
class GraduationRequirementAdmin(ImportExportModelAdmin):
    list_display = ('major', 'sequence', 'content')
    list_filter = ('major',)

@admin.register(IndicatorPoint)
class IndicatorPointAdmin(ImportExportModelAdmin):
    resource_class = IndicatorPointResource
    list_display = ('requirement', 'sequence', 'content')

@admin.register(Course)
class CourseAdmin(ImportExportModelAdmin):
    resource_class = CourseResource
    list_display = ('code', 'name', 'credits', 'major')
    list_filter = ('major',)
    search_fields = ('code', 'name')

@admin.register(CourseSupport)
class CourseSupportAdmin(ImportExportModelAdmin):
    resource_class = CourseSupportResource
    list_display = ('course', 'indicator', 'weight')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    # 列表页展示的字段
    list_display = ('user', 'model_name', 'action', 'object_repr', 'version', 'timestamp')
    # 右侧增加过滤侧边栏
    list_filter = ('action', 'model_name', 'user')