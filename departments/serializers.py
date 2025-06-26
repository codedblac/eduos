from rest_framework import serializers
from .models import Department, DepartmentUser, Subject, DepartmentAnnouncement, DepartmentLeaveApproval, DepartmentPerformanceNote
from accounts.serializers import UserSummarySerializer
from institutions.serializers import InstitutionBasicSerializer


class DepartmentSerializer(serializers.ModelSerializer):
    institution = InstitutionBasicSerializer(read_only=True)

    class Meta:
        model = Department
        fields = '__all__'


class DepartmentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['name', 'code', 'institution', 'description', 'is_academic', 'type']


class DepartmentUserSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = DepartmentUser
        fields = '__all__'


class DepartmentUserCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentUser
        fields = ['user', 'department', 'role', 'is_active']


class SubjectSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    assigned_teacher = UserSummarySerializer(read_only=True)

    class Meta:
        model = Subject
        fields = '__all__'


class SubjectCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'department', 'assigned_teacher', 'description',
                  'is_examable', 'is_mapped_to_timetable', 'is_linked_to_elearning']


class DepartmentAnnouncementSerializer(serializers.ModelSerializer):
    created_by = UserSummarySerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = DepartmentAnnouncement
        fields = '__all__'


class DepartmentAnnouncementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentAnnouncement
        fields = ['title', 'message', 'department']


class DepartmentLeaveApprovalSerializer(serializers.ModelSerializer):
    approved_by = UserSummarySerializer(read_only=True)
    staff = UserSummarySerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = DepartmentLeaveApproval
        fields = '__all__'


class DepartmentPerformanceNoteSerializer(serializers.ModelSerializer):
    created_by = UserSummarySerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = DepartmentPerformanceNote
        fields = '__all__'


class DepartmentPerformanceNoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentPerformanceNote
        fields = ['subject', 'note']
