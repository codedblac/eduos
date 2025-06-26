from django.contrib import admin
from .models import (
    Currency, FundSource, ExpenseCategory, Budget, Income, Expense,
    Refund, Waiver, StudentWallet, WalletTransaction,
    StudentFinanceSnapshot, TransactionLog, ApprovalRequest,
    FinanceNotification, AnomalyFlag, ScholarshipCandidate,
    RecurringTransaction, JournalEntry, AuditTrail
)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'symbol', 'exchange_rate']
    search_fields = ['code', 'symbol']


@admin.register(FundSource)
class FundSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name', 'description']


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['institution', 'academic_year', 'term', 'total_income_estimate', 'total_expense_estimate', 'created_by', 'created_at']
    list_filter = ['academic_year', 'term', 'institution']
    search_fields = ['institution__name']


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'received_on', 'received_by', 'budget', 'source']
    list_filter = ['received_on', 'budget__institution']
    search_fields = ['description']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'spent_on', 'spent_by', 'budget', 'category']
    list_filter = ['spent_on', 'category']
    search_fields = ['description']


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['student', 'amount', 'status', 'requested_on', 'approved_by']
    list_filter = ['status', 'requested_on']
    search_fields = ['student__full_name']


@admin.register(Waiver)
class WaiverAdmin(admin.ModelAdmin):
    list_display = ['student', 'amount', 'term', 'academic_year', 'approved_by']
    list_filter = ['term', 'academic_year']
    search_fields = ['student__full_name']


@admin.register(StudentWallet)
class StudentWalletAdmin(admin.ModelAdmin):
    list_display = ['student', 'balance', 'updated_at']
    search_fields = ['student__full_name']


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'type', 'amount', 'reference', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['reference']


@admin.register(StudentFinanceSnapshot)
class StudentFinanceSnapshotAdmin(admin.ModelAdmin):
    list_display = ['student', 'academic_year', 'term', 'total_invoiced', 'total_paid', 'balance', 'last_updated']
    list_filter = ['academic_year', 'term']
    search_fields = ['student__full_name']


@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'actor', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['actor__username', 'details']


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ['request_type', 'reference_id', 'requested_by', 'approved_by', 'status', 'requested_on']
    list_filter = ['status', 'request_type']
    search_fields = ['reference_id']


@admin.register(FinanceNotification)
class FinanceNotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'message', 'created_at', 'read']
    list_filter = ['read', 'created_at']
    search_fields = ['recipient__username']


@admin.register(AnomalyFlag)
class AnomalyFlagAdmin(admin.ModelAdmin):
    list_display = ['student', 'description', 'flagged_on', 'resolved']
    list_filter = ['resolved']
    search_fields = ['student__full_name']


@admin.register(ScholarshipCandidate)
class ScholarshipCandidateAdmin(admin.ModelAdmin):
    list_display = ['student', 'academic_year', 'score', 'need_score', 'recommended_by_ai']
    list_filter = ['academic_year', 'recommended_by_ai']
    search_fields = ['student__full_name']


@admin.register(RecurringTransaction)
class RecurringTransactionAdmin(admin.ModelAdmin):
    list_display = ['type', 'description', 'amount', 'frequency', 'start_date', 'next_run', 'active']
    list_filter = ['type', 'frequency', 'active']
    search_fields = ['description']


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['date', 'description', 'debit_account', 'credit_account', 'amount', 'posted_by']
    list_filter = ['date']
    search_fields = ['description']


@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'object_id', 'action', 'performed_by', 'timestamp']
    list_filter = ['model_name', 'action']
    search_fields = ['model_name', 'notes']

