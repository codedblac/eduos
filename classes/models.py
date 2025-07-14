from django.db import models
from django.conf import settings
from institutions.models import Institution
from academics.models import AcademicYear

User = settings.AUTH_USER_MODEL


class ClassLevel(models.Model):
    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, related_name='class_levels'
    )
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20, unique=True)
    order = models.PositiveIntegerField(default=1)

    description = models.TextField(blank=True, null=True)
    is_graduating_level = models.BooleanField(default=False)
    requires_national_exam = models.BooleanField(default=False)

    default_promotion_class = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='previous_level'
    )

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='classlevels_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='classlevels_updated')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('institution', 'name')
        ordering = ['order', 'name']
        verbose_name = 'Class Level'
        verbose_name_plural = 'Class Levels'

    def __str__(self):
        return f"{self.name} ({self.institution.name})"


class Stream(models.Model):
    class_level = models.ForeignKey(
        ClassLevel, on_delete=models.CASCADE, related_name='streams'
    )
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=20, unique=True)
    order = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, null=True)

    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.CASCADE, related_name='streams'
    )
    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, related_name='streams'
    )
    capacity = models.PositiveIntegerField(default=60)

    
    class_teacher = models.ForeignKey(
        'teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='streams_as_class_teacher'
    )

    is_active = models.BooleanField(default=True)
    auto_promote_enabled = models.BooleanField(default=True)

    average_score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    average_attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    rank_within_class_level = models.PositiveIntegerField(null=True, blank=True)
    last_ai_evaluation = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='streams_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='streams_updated')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('class_level', 'name', 'academic_year', 'institution')
        ordering = ['academic_year', 'class_level__order', 'order', 'name']
        verbose_name = 'Stream'
        verbose_name_plural = 'Streams'

    def __str__(self):
        return f"{self.name} ({self.class_level.name}) - {self.academic_year.name}"

    def current_student_count(self):
        return self.students.count()

    def is_over_capacity(self):
        return self.current_student_count() > self.capacity
