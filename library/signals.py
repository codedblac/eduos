from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from .models import (
    BorrowTransaction, Fine, BookIssueReport,
    BookRating, BookUsageStat
)
from .tasks import (
    log_book_usage_statistics,
    auto_generate_fines,
    notify_overdue_books,
    notify_damaged_or_lost_books
)
from notifications.utils import send_notification


@receiver(post_save, sender=BorrowTransaction)
def handle_borrow_transaction_save(sender, instance, created, **kwargs):
    """
    Trigger notifications and background tasks when a transaction is created or updated.
    """
    book = instance.book_copy.book
    accession = instance.book_copy.accession_number
    due = instance.due_date

    if created:
        send_notification(
            user=instance.user,
            title="📚 Book Borrowed",
            message=f"You borrowed '{book.title}' (Accession: {accession}). Due on {due}.",
            target="library"
        )
    else:
        if instance.returned_on:
            send_notification(
                user=instance.user,
                title="✅ Book Returned",
                message=f"Thanks for returning '{book.title}'.",
                target="library"
            )

    # Background updates
    log_book_usage_statistics.delay()
    auto_generate_fines.delay()


@receiver(post_save, sender=BookIssueReport)
def handle_book_issue_report(sender, instance, created, **kwargs):
    """
    Notify assigned user or librarian when a new issue is reported.
    """
    if created and not instance.resolved:
        notify_damaged_or_lost_books.delay()


@receiver(post_save, sender=BookRating)
def handle_book_rating_save(sender, instance, created, **kwargs):
    """
    Recalculate usage stats when a book rating is added or updated.
    """
    log_book_usage_statistics.delay()


@receiver(post_delete, sender=Fine)
def handle_fine_deleted(sender, instance, **kwargs):
    """
    Notify user if a fine has been deleted/waived manually.
    """
    book = instance.transaction.book_copy.book
    send_notification(
        user=instance.transaction.user,
        title="💸 Fine Cleared",
        message=f"Your fine for '{book.title}' has been cleared.",
        target="library"
    )


@receiver(post_save, sender=Fine)
def handle_fine_created(sender, instance, created, **kwargs):
    """
    Notify user when a fine is created.
    """
    if created:
        book = instance.transaction.book_copy.book
        due = instance.transaction.due_date
        amount = instance.amount

        send_notification(
            user=instance.transaction.user,
            title="💰 Fine Issued",
            message=f"You have been fined {amount} for not returning '{book.title}' by {due}.",
            target="library"
        )
