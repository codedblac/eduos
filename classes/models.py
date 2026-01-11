from django.db import models
from django.conf import settings

from institutions.models import Institution
from academics.models import AcademicYear

User = settings.AUTH_USER_MODEL


# ======================================================
# CLASS LEVEL (Grade / Form)
# ======================================================
class ClassLevel(models.Model):
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="class_levels",
    )

    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20)
    order = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, null=True)

    # Academic behavior
    is_graduating_level = models.BooleanField(default=False)
    requires_national_exam = models.BooleanField(default=False)

    # Promotion logic
    default_promotion_class = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="previous_levels",
    )

    # Ownership
    class_teacher = models.ForeignKey(
        "teachers.Teacher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classes_as_class_teacher",
    )

    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classlevels_created",
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classlevels_updated",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("institution", "code")
        ordering = ["order", "name"]
        verbose_name = "Class Level"
        verbose_name_plural = "Class Levels"

    def __str__(self):
        return f"{self.name} ({self.institution.name})"


# ======================================================
# STREAM (Subclass of a ClassLevel, Year-specific)
# ======================================================
class Stream(models.Model):
    class_level = models.ForeignKey(
        ClassLevel,
        on_delete=models.CASCADE,
        related_name="streams",
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="streams",
    )

    name = models.CharField(max_length=30)
    code = models.CharField(max_length=20)
    order = models.PositiveIntegerField(default=1)

    description = models.TextField(blank=True, null=True)
    capacity = models.PositiveIntegerField(default=60)

    # Ownership
    stream_teacher = models.ForeignKey(
        "teachers.Teacher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="streams_as_stream_teacher",
    )

    # Lifecycle
    is_active = models.BooleanField(default=True)
    auto_promote_enabled = models.BooleanField(default=True)

    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="streams_created",
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="streams_updated",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("class_level", "academic_year", "code")
        ordering = [
            "academic_year",
            "class_level__order",
            "order",
            "name",
        ]
        verbose_name = "Stream"
        verbose_name_plural = "Streams"

    def __str__(self):
        return f"{self.name} ({self.class_level.name}) - {self.academic_year.name}"

    # --------------------------------------------------
    # ✅ SAFE COMPUTED FIELDS (NO NAME COLLISION)
    # --------------------------------------------------
    @property
    def current_student_count(self):
        """
        Count ONLY active students.
        Safe fallback if queryset annotation is missing.
        """
        return self.enrollments_classes.filter(status="active").count()

    def is_over_capacity_flag(self):
        """
        Boolean method (NOT property) to avoid DRF/Admin collision.
        """
        return self.current_student_count > self.capacity


# ======================================================
# STUDENT ↔ STREAM ENROLLMENT
# ======================================================
class StudentStreamEnrollment(models.Model):
    STATUS_CHOICES = (
        ("active", "Active"),
        ("transferred", "Transferred"),
        ("completed", "Completed"),
        ("withdrawn", "Withdrawn"),
    )

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="stream_enrollments_classes",
    )

    stream = models.ForeignKey(
        Stream,
        on_delete=models.CASCADE,
        related_name="enrollments_classes",
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="student_enrollments_classes",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
    )

    date_assigned = models.DateField(auto_now_add=True)
    date_left = models.DateField(null=True, blank=True)

    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stream_assignments_classes",
    )

    class Meta:
        unique_together = ("student", "academic_year")
        indexes = [
            models.Index(fields=["student", "academic_year"]),
            models.Index(fields=["stream", "status"]),
        ]
        verbose_name = "Student Stream Enrollment"
        verbose_name_plural = "Student Stream Enrollments"

    def __str__(self):
        return f"{self.student} → {self.stream}"


# ======================================================
# STREAM ANALYTICS
# ======================================================
class StreamAnalytics(models.Model):
    stream = models.ForeignKey(
        Stream,
        on_delete=models.CASCADE,
        related_name="analytics",
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
    )

    total_students = models.PositiveIntegerField()
    average_score = models.DecimalField(max_digits=6, decimal_places=2)
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2)
    discipline_index = models.DecimalField(max_digits=5, decimal_places=2)

    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("stream", "academic_year")
        ordering = ["-calculated_at"]
        verbose_name = "Stream Analytics"
        verbose_name_plural = "Stream Analytics"


# ======================================================
# CLASS LEVEL ANALYTICS
# ======================================================
class ClassLevelAnalytics(models.Model):
    class_level = models.ForeignKey(
        ClassLevel,
        on_delete=models.CASCADE,
        related_name="analytics",
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
    )

    total_students = models.PositiveIntegerField()
    average_score = models.DecimalField(max_digits=6, decimal_places=2)

    top_stream = models.ForeignKey(
        Stream,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("class_level", "academic_year")
        ordering = ["-calculated_at"]
        verbose_name = "Class Level Analytics"
        verbose_name_plural = "Class Level Analytics"
