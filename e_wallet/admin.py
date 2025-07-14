from django.contrib import admin
from .models import (
    Wallet,
    WalletTransaction,
    MicroFee,
    MicroFeePayment,
    WalletTopUpRequest,
    WalletPolicy,
    WalletAuditLog
)


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('student', 'institution', 'balance', 'is_active', 'last_updated')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'student__admission_number')
    list_filter = ('is_active', 'institution')
    readonly_fields = ('last_updated',)


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'type', 'amount', 'purpose', 'reference', 'initiated_by', 'created_at')
    search_fields = ('wallet__student__user__first_name', 'wallet__student__user__last_name', 'reference')
    list_filter = ('type', 'created_at')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)


@admin.register(MicroFee)
class MicroFeeAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'amount', 'due_date', 'class_level', 'stream', 'is_active', 'created_at')
    search_fields = ('title', 'teacher__first_name', 'teacher__last_name')
    list_filter = ('due_date', 'class_level', 'stream', 'is_active')
    readonly_fields = ('created_at',)


@admin.register(MicroFeePayment)
class MicroFeePaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'micro_fee', 'amount_paid', 'paid_via_wallet', 'payment_reference', 'paid_on')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'micro_fee__title')
    list_filter = ('paid_via_wallet', 'paid_on')
    date_hierarchy = 'paid_on'
    readonly_fields = ('paid_on',)


@admin.register(WalletTopUpRequest)
class WalletTopUpRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'parent', 'amount', 'payment_method', 'confirmed', 'created_at', 'confirmed_at')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'parent__first_name', 'parent__last_name')
    list_filter = ('payment_method', 'confirmed', 'created_at')
    readonly_fields = ('created_at', 'confirmed_at')


@admin.register(WalletPolicy)
class WalletPolicyAdmin(admin.ModelAdmin):
    list_display = ('institution', 'max_daily_spend', 'withdrawal_allowed', 'auto_lock_enabled', 'lock_threshold', 'created_at')
    list_filter = ('institution', 'withdrawal_allowed', 'auto_lock_enabled')
    readonly_fields = ('created_at',)


@admin.register(WalletAuditLog)
class WalletAuditLogAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'action', 'actor', 'timestamp')
    search_fields = ('wallet__student__user__first_name', 'wallet__student__user__last_name', 'actor__first_name', 'actor__last_name')
    list_filter = ('action', 'timestamp')
    readonly_fields = ('timestamp',)
