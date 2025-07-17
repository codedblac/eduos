from django.contrib import admin
from .models import (
    Currency, CurrencyRateHistory, FundSource, ExpenseCategory, Budget,
    Income, Expense, InvoiceLineItem, Refund, Waiver, StudentWallet,
    WalletTransaction, StudentFinanceSnapshot, StudentInvoice, TransactionLog,
    ApprovalRequest, FinanceNotification, AnomalyFlag, ScholarshipCandidate,
    RecurringTransaction, JournalEntry, AuditTrail, ChartOfAccount
)

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'symbol', 'exchange_rate', 'is_active', 'is_default']
    list_filter = ['is_active', 'is_default']


@admin.register(CurrencyRateHistory)
class CurrencyRateHistoryAdmin(admin.ModelAdmin):
    list_display = ['currency', 'rate', 'recorded_at']


@admin.register(FundSource)
class FundSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'description']
    list_filter = ['category']


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['institution', 'academic_year', 'term', 'total_income_estimate', 'total_expense_estimate', 'status']
    list_filter = ['institution', 'academic_year', 'term', 'status']


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['budget', 'description', 'amount', 'received_on', 'received_by']
    list_filter = ['received_on', 'budget']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['budget', 'description', 'amount', 'spent_on', 'spent_by']
    list_filter = ['spent_on', 'budget']


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['student', 'amount', 'status', 'requested_on']
    list_filter = ['status', 'requested_on']


@admin.register(Waiver)
class WaiverAdmin(admin.ModelAdmin):
    list_display = ['student', 'amount', 'approved_by', 'approved_on']
    list_filter = ['term', 'academic_year']


@admin.register(StudentWallet)
class StudentWalletAdmin(admin.ModelAdmin):
    list_display = ['student', 'balance', 'is_frozen', 'updated_at']


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'amount', 'type', 'reference', 'status', 'created_at']
    list_filter = ['type', 'status']


@admin.register(StudentFinanceSnapshot)
class StudentFinanceSnapshotAdmin(admin.ModelAdmin):
    list_display = ['student', 'academic_year', 'term', 'total_invoiced', 'total_paid', 'balance']


@admin.register(StudentInvoice)
class StudentInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'student', 'term', 'academic_year', 'total_amount', 'balance', 'status']


@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'actor', 'timestamp']


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ['request_type', 'content_type', 'object_id', 'status', 'requested_by', 'approved_by', 'requested_on']
    raw_id_fields = ['content_type']  # ✅ safer for GenericForeignKey


@admin.register(FinanceNotification)
class FinanceNotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'type', 'created_at', 'read']
    list_filter = ['type', 'read']


@admin.register(AnomalyFlag)
class AnomalyFlagAdmin(admin.ModelAdmin):
    list_display = ['student', 'description', 'flagged_on', 'resolved']
    list_filter = ['resolved']


@admin.register(ScholarshipCandidate)
class ScholarshipCandidateAdmin(admin.ModelAdmin):
    list_display = ['student', 'academic_year', 'score', 'need_score', 'recommended_by_ai']


@admin.register(RecurringTransaction)
class RecurringTransactionAdmin(admin.ModelAdmin):
    list_display = ['type', 'description', 'amount', 'frequency', 'start_date', 'next_run', 'active']


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['date', 'description', 'debit_account', 'credit_account', 'amount', 'is_reconciled']


@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'action', 'performed_by', 'timestamp']


@admin.register(ChartOfAccount)
class ChartOfAccountAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'type', 'is_active']
    list_filter = ['type', 'is_active']


@admin.register(InvoiceLineItem)
class InvoiceLineItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'description', 'amount']
