from rest_framework import serializers
from .models import (
    Wallet,
    WalletTransaction,
    MicroFee,
    MicroFeePayment,
    WalletTopUpRequest,
    WalletPolicy,
    WalletAuditLog
)
from students.models import Student
from accounts.models import CustomUser

from .models import MicroFeeAssignment 

class MicroFeeAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MicroFeeAssignment
        fields = '__all__'
        
class WalletSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        fields = '__all__'

    def get_student_name(self, obj):
        if obj.student and hasattr(obj.student, 'user'):
            return f"{obj.student.user.first_name} {obj.student.user.last_name}"
        return ""


class WalletTransactionSerializer(serializers.ModelSerializer):
    initiated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = WalletTransaction
        fields = '__all__'

    def get_initiated_by_name(self, obj):
        if obj.initiated_by:
            return f"{obj.initiated_by.first_name} {obj.initiated_by.last_name}"
        return ""


class MicroFeeSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = MicroFee
        fields = '__all__'

    def get_teacher_name(self, obj):
        if obj.teacher:
            return f"{obj.teacher.first_name} {obj.teacher.last_name}"
        return ""


class MicroFeePaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = MicroFeePayment
        fields = '__all__'

    def get_student_name(self, obj):
        if obj.student and hasattr(obj.student, 'user'):
            return f"{obj.student.user.first_name} {obj.student.user.last_name}"
        return ""


class WalletTopUpRequestSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model = WalletTopUpRequest
        fields = '__all__'

    def get_student_name(self, obj):
        if obj.student and hasattr(obj.student, 'user'):
            return f"{obj.student.user.first_name} {obj.student.user.last_name}"
        return ""

    def get_parent_name(self, obj):
        if obj.parent:
            return f"{obj.parent.first_name} {obj.parent.last_name}"
        return ""


class WalletPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletPolicy
        fields = '__all__'


class WalletAuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.SerializerMethodField()

    class Meta:
        model = WalletAuditLog
        fields = '__all__'

    def get_actor_name(self, obj):
        if obj.actor:
            return f"{obj.actor.first_name} {obj.actor.last_name}"
        return ""
