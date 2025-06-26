from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Teacher

User = get_user_model()

class TeacherSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        source='user', queryset=User.objects.all(), allow_null=True, required=False
    )
    subjects = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    classes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    timetable_pdf = serializers.FileField(read_only=True)  # ✅ Added for timetable visibility

    class Meta:
        model = Teacher
        fields = [
            'id', 'user_id', 'institution', 'first_name', 'last_name', 'email',
            'phone', 'photo', 'subjects', 'classes', 'is_active',
            'timetable_pdf',  
            'date_joined', 'updated_at',
        ]
        read_only_fields = ['date_joined', 'updated_at', 'timetable_pdf']
