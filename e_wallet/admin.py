# e_wallet/admin.py

from django.contrib import admin
from .models import (
    MicroFeeAssignment,
    Wallet,
    WalletTransaction,
    MicroFee,
    MicroFeePayment,
    WalletTopUpRequest,
    WalletReminder,
    WalletPolicy,
    WalletAuditLog,
)


@admin.register(MicroFeeAssignment)
class MicroFeeAssignmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'term', 'fee_type', 'amount', 'is_paid', 'assigned_by', 'assigned_at')
    list_filter = ('fee_type', 'is_paid', 'term')
    search_fields = ('student__full_name', 'fee_type', 'assigned_by__username')
    readonly_fields = ('assigned_at', 'paid_at')


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('student', 'balance', 'is_active', 'institution', 'last_updated')
    search_fields = ('student__full_name', 'institution__name')


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'type', 'amount', 'purpose', 'initiated_by', 'created_at')
    list_filter = ('type',)
    search_fields = ('wallet__student__full_name', 'purpose', 'reference')


@admin.register(MicroFee)
class MicroFeeAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'teacher', 'due_date', 'class_level', 'stream', 'is_active')
    list_filter = ('class_level', 'stream', 'is_active')
    search_fields = ('title', 'teacher__username')


@admin.register(MicroFeePayment)
class MicroFeePaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'micro_fee', 'amount_paid', 'paid_via_wallet', 'paid_on')
    search_fields = ('student__full_name', 'micro_fee__title')


@admin.register(WalletTopUpRequest)
class WalletTopUpRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'payment_method', 'confirmed', 'created_at', 'confirmed_at')
    list_filter = ('payment_method', 'confirmed')
    search_fields = ('student__full_name',)


@admin.register(WalletReminder)
class WalletReminderAdmin(admin.ModelAdmin):
    list_display = ('user', 'resolved', 'sent', 'sent_at', 'created_at')
    list_filter = ('resolved', 'sent')
    search_fields = ('user__username',)


@admin.register(WalletPolicy)
class WalletPolicyAdmin(admin.ModelAdmin):
    list_display = ('institution', 'max_daily_spend', 'withdrawal_allowed', 'auto_lock_enabled', 'lock_threshold')


@admin.register(WalletAuditLog)
class WalletAuditLogAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'action', 'actor', 'timestamp')
    search_fields = ('wallet__student__full_name', 'action', 'actor__username')
    readonly_fields = ('timestamp',)

