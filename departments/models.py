from django.db import models
from django.conf import settings
from institutions.models import Institution


class Department(models.Model):
    ACADEMIC = 'academic'
    CO_CURRICULAR = 'co-curricular'

    DEPARTMENT_TYPE_CHOICES = [
        (ACADEMIC, 'Academic'),
        (CO_CURRICULAR, 'Co-curricular'),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, blank=True, null=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='departments')
    description = models.TextField(blank=True, null=True)
    is_academic = models.BooleanField(default=True)
    type = models.CharField(max_length=20, choices=DEPARTMENT_TYPE_CHOICES, default=ACADEMIC)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('name', 'institution')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.institution.name})"


class DepartmentUser(models.Model):
    HOD = 'hod'
    DEPUTY_HOD = 'deputy_hod'
    MEMBER = 'member'
    HEAD_OF_SUBJECT = 'hos'

    ROLE_CHOICES = [
        (HOD, 'Head of Department'),
        (DEPUTY_HOD, 'Deputy Head of Department'),
        (HEAD_OF_SUBJECT, 'Head of Subject'),
        (MEMBER, 'Member'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=MEMBER)
    is_active = models.BooleanField(default=True)
    assigned_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'department')
        ordering = ['department', 'role']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department.name} ({self.role})"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subjects')
    assigned_teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_subjects')
    description = models.TextField(blank=True, null=True)

    is_examable = models.BooleanField(default=True, help_text="Used in exams analysis")
    is_mapped_to_timetable = models.BooleanField(default=False, help_text="Linked in timetable")
    is_linked_to_elearning = models.BooleanField(default=False, help_text="Linked to e-learning content")

    class Meta:
        unique_together = ('name', 'department')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.department.name}"


class DepartmentAnnouncement(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    visible_to_roles = models.JSONField(default=list)  # e.g., ['member', 'hos']

    def __str__(self):
        return f"{self.title} - {self.department.name}"


class DepartmentPerformanceNote(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='performance_notes')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    note = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_notes')
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student} - {self.department.name}"


class DepartmentLeaveApproval(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    staff_member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='dept_leave_approvals')
    decision_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.staff_member} - {self.status}"
