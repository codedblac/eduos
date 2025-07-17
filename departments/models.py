from django.db import models
from django.conf import settings
from institutions.models import Institution
from classes.models import ClassLevel
from academics.models import Term, AcademicYear

User = settings.AUTH_USER_MODEL

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
    parent_department = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='sub_departments')
    description = models.TextField(blank=True, null=True)
    is_academic = models.BooleanField(default=True)
    type = models.CharField(max_length=20, choices=DEPARTMENT_TYPE_CHOICES, default=ACADEMIC)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    is_deleted = models.BooleanField(default=False)

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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=MEMBER)
    is_active = models.BooleanField(default=True)
    assigned_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'department')
        ordering = ['department', 'role']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department.name} ({self.role})"


class DepartmentRoleAssignmentHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=DepartmentUser.ROLE_CHOICES)
    assigned_on = models.DateTimeField()
    revoked_on = models.DateTimeField(null=True, blank=True)


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subjects')
    assigned_teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_subjects')
    class_levels = models.ManyToManyField(ClassLevel, blank=True, related_name='subjects')
    description = models.TextField(blank=True, null=True)
    is_examable = models.BooleanField(default=True)
    is_mapped_to_timetable = models.BooleanField(default=False)
    is_linked_to_elearning = models.BooleanField(default=False)

    class Meta:
        unique_together = ('name', 'department')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.department.name}"


class DepartmentAnnouncement(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.SET_NULL, null=True, blank=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True, blank=True)
    visible_to_roles = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)


class DepartmentPerformanceNote(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='performance_notes')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    note = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_notes')
    term = models.ForeignKey(Term, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)


class DepartmentLeaveApproval(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    staff_member = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='dept_leave_approvals')
    decision_date = models.DateTimeField(null=True, blank=True)


class DepartmentMeeting(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    agenda = models.TextField()
    minutes = models.TextField(blank=True)
    date = models.DateField()
    conducted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class DepartmentKPI(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    target = models.CharField(max_length=255)
    achieved = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='kpi_reviews')
    reviewed_at = models.DateTimeField(null=True, blank=True)


class DepartmentBudget(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    fiscal_year = models.CharField(max_length=20)
    amount_allocated = models.DecimalField(max_digits=12, decimal_places=2)
    amount_used = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)


class DepartmentResource(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    acquired_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('in_use', 'In Use'), ('damaged', 'Damaged'), ('retired', 'Retired')], default='in_use')


class DepartmentAuditLog(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)


class DepartmentDocument(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='department_documents/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_on = models.DateTimeField(auto_now_add=True)


class DepartmentGoal(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    target_date = models.DateField()
    progress = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('achieved', 'Achieved')])
    created_at = models.DateTimeField(auto_now_add=True)


class DepartmentAnnualPlan(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    year = models.CharField(max_length=10)
    summary = models.TextField()
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reviewed_on = models.DateTimeField(null=True, blank=True)


class DepartmentTask(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=[('todo', 'To Do'), ('in_progress', 'In Progress'), ('done', 'Done')])
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)


class DepartmentAnalyticsSnapshot(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.SET_NULL, null=True)
    kpi_score = models.DecimalField(max_digits=5, decimal_places=2)
    staff_attendance = models.DecimalField(max_digits=5, decimal_places=2)
    student_performance_index = models.DecimalField(max_digits=5, decimal_places=2)
    snapshot_date = models.DateField(auto_now_add=True)
