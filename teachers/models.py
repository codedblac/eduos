from django.db import models
from django.conf import settings

class Teacher(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='teacher_profile'
    )
    institution = models.ForeignKey(
        'institutions.Institution',
        on_delete=models.CASCADE,
        related_name='teachers'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    photo = models.ImageField(upload_to='teachers/photos/', blank=True, null=True)

    # ✅ Use the through model to avoid reverse accessor conflict
    subjects = models.ManyToManyField(
        'subjects.Subject',
        through='subjects.SubjectTeacher',
        related_name='assigned_teachers',
        blank=True
    )
    classes = models.ManyToManyField(
        'classes.Stream',
        blank=True,
        related_name='teachers'
    )

    is_active = models.BooleanField(default=True)
    date_joined = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ✅ New: Auto-generated timetable PDF field
    timetable_pdf = models.FileField(upload_to='teachers/timetables/', blank=True, null=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        unique_together = ('institution', 'email')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.institution.name})"
