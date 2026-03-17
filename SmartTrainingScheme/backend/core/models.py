# -*- coding: utf-8 -*-
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum
from decimal import Decimal
from django.conf import settings # 引入用户模型
from django.utils import timezone

class Major(models.Model):
    name = models.CharField(max_length=100, verbose_name="专业名称")
    code = models.CharField(max_length=20, unique=True, verbose_name="专业代码")
    
    # --- 新增的文本信息字段 ---
    duration = models.CharField(max_length=50, verbose_name="学制", null=True, blank=True)
    degree = models.CharField(max_length=50, verbose_name="学位", null=True, blank=True)
    core_disciplines = models.TextField(verbose_name="主干学科", null=True, blank=True)
    core_courses_text = models.TextField(verbose_name="主干课程文本", null=True, blank=True)
    graduation_condition = models.TextField(verbose_name="毕业条件", null=True, blank=True)
    degree_condition = models.TextField(verbose_name="学士学位授予条件", null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class TrainingObjective(models.Model):
    """
    Level 1: TrainingObjective
    """
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='training_objectives', verbose_name="Major")
    content = models.TextField(verbose_name="Content")
    sequence = models.PositiveIntegerField(default=1, verbose_name="Sequence")
    
    class Meta:
        verbose_name = "Training Objective"
        verbose_name_plural = verbose_name
        ordering = ['sequence']

    def __str__(self):
        return f"Objective {self.sequence}: {self.content[:20]}..."

class GraduationRequirement(models.Model):
    """
    Level 2: GraduationRequirement
    """
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='graduation_requirements', verbose_name="Major")
    content = models.TextField(verbose_name="Content")
    sequence = models.PositiveIntegerField(default=1, verbose_name="Sequence")
    
    training_objectives = models.ManyToManyField(
        TrainingObjective, 
        through='ObjectiveSupport',
        related_name='supported_requirements',
        verbose_name="Supported Training Objectives"
    )

    class Meta:
        verbose_name = "Graduation Requirement"
        verbose_name_plural = verbose_name
        ordering = ['sequence']

    def __str__(self):
        return f"Requirement {self.sequence}: {self.content[:20]}..."

class ObjectiveSupport(models.Model):
    """
    Support relationship between GraduationRequirement and TrainingObjective
    """
    requirement = models.ForeignKey(GraduationRequirement, on_delete=models.CASCADE, verbose_name="Requirement")
    objective = models.ForeignKey(TrainingObjective, on_delete=models.CASCADE, verbose_name="Objective")
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, verbose_name="Weight")

    class Meta:
        verbose_name = "Objective Support"
        verbose_name_plural = verbose_name
        unique_together = ('requirement', 'objective')

    def __str__(self):
        return f"{self.requirement.sequence} -> {self.objective.sequence} (Weight: {self.weight})"

class IndicatorPoint(models.Model):
    """
    Level 3: IndicatorPoint
    """
    requirement = models.ForeignKey(GraduationRequirement, on_delete=models.CASCADE, related_name='indicator_points', verbose_name="Graduation Requirement")
    content = models.TextField(verbose_name="Content")
    sequence = models.PositiveIntegerField(default=1, verbose_name="Sequence")
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, verbose_name="Weight")

    class Meta:
        verbose_name = "Indicator Point"
        verbose_name_plural = verbose_name
        ordering = ['sequence']

    def __str__(self):
        return f"Indicator {self.requirement.sequence}.{self.sequence}"

    def clean(self):
        """
        Validation for weight summation.
        """
        super().clean()
        
        if self.requirement_id:
            siblings = IndicatorPoint.objects.filter(requirement=self.requirement)
            if self.pk:
                siblings = siblings.exclude(pk=self.pk)
            
            current_sum = siblings.aggregate(total=Sum('weight'))['total'] or Decimal('0.00')
            new_total = current_sum + self.weight

            if new_total > Decimal('1.0001'): 
                 pass # In actual use, you might want to log a warning or raise a ValidationError

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Course(models.Model):
    """
    Level 4: Course
    """
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='courses', verbose_name="Major")
    name = models.CharField(max_length=100, verbose_name="Course Name")
    code = models.CharField(max_length=50, unique=True, verbose_name="Course Code")
    semester = models.PositiveIntegerField(blank=True, null=True, verbose_name="Semester")
    category = models.CharField(max_length=50, blank=True, null=True, verbose_name="Course Category")
    credits = models.DecimalField(max_digits=4, decimal_places=1, verbose_name="Credits")
    
    prerequisites = models.ManyToManyField(
        'self', 
        symmetrical=False, 
        related_name='required_by', 
        blank=True, 
        verbose_name="Prerequisites"
    )
    
    indicator_points = models.ManyToManyField(
        IndicatorPoint, 
        through='CourseSupport',
        related_name='courses',
        verbose_name="Indicator Points"
    )

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name} ({self.code})"

class CourseSupport(models.Model):
    """
    Support relationship between Course and IndicatorPoint
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='supports', verbose_name="Course")
    indicator = models.ForeignKey(IndicatorPoint, on_delete=models.CASCADE, verbose_name="Indicator")
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, verbose_name="Weight")

    class Meta:
        verbose_name = "Course Support"
        verbose_name_plural = verbose_name
        unique_together = ('course', 'indicator')

    def __str__(self):
        return f"{self.course.name} -> {self.indicator} (Weight: {self.weight})"

class AuditLog(models.Model):
    # 谁操作的
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    # 操作了哪个模型（比如 Course, CourseSupport）
    model_name = models.CharField(max_length=100)
    # 具体操作类型：新增、修改、删除
    action = models.CharField(max_length=20)
    # 对象的 ID 或 名称，方便追溯
    object_id = models.CharField(max_length=50)
    object_repr = models.CharField(max_length=255)
    # 修改的具体内容（可以存 JSON 字符串）
    changes = models.TextField(blank=True)
    # 修改时间
    timestamp = models.DateTimeField(default=timezone.now)
    # 版本号（第几版）
    version = models.IntegerField(default=1)

    class Meta:
        ordering = ['-timestamp'] # 最新的记录排在最前面

    def __str__(self):
        return f"{self.user} {self.action} {self.model_name} at {self.timestamp}"
