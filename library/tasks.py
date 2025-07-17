from celery import shared_task
from django.utils import timezone
from django.db.models import Avg, Count, Q, F
from datetime import timedelta

from .models import (
    Book, BookUsageStat, BorrowTransaction, Fine,
    BookCopy, BookRating, BookIssueReport, LibraryMember
)
from notifications.utils import send_notification


@shared_task
def notify_overdue_books():
    """
    Notify users about overdue borrowed books.
    """
    today = timezone.now().date()
    overdue_transactions = BorrowTransaction.objects.filter(
        returned_on__isnull=True,
        due_date__lt=today
    ).select_related('user', 'book_copy__book')

    for tx in overdue_transactions:
        send_notification(
            user=tx.user,
            title="📚 Overdue Book Alert",
            message=f"You have not returned '{tx.book_copy.book.title}' "
                    f"(Accession: {tx.book_copy.accession_number}). "
                    f"It was due on {tx.due_date}.",
            target="library"
        )


@shared_task
def auto_generate_fines():
    """
    Automatically generate fines for overdue books that have not been returned and have no fine record yet.
    """
    today = timezone.now().date()
    overdue_transactions = BorrowTransaction.objects.filter(
        returned_on__isnull=True,
        due_date__lt=today,
        fine__isnull=True
    ).select_related('book_copy__book', 'user')

    for tx in overdue_transactions:
        days_overdue = (today - tx.due_date).days
        amount = days_overdue * 10  # TODO: Make fine rate configurable per institution

        Fine.objects.create(
            transaction=tx,
            amount=amount,
            institution=tx.user.institution if hasattr(tx.user, 'institution') else None
        )


@shared_task
def log_book_usage_statistics():
    """
    Recalculate and log daily book usage stats.
    Should be scheduled to run daily (e.g. via Celery Beat).
    """
    today = timezone.now().date()
    books = Book.objects.filter(is_active=True)

    for book in books:
        borrow_count = BorrowTransaction.objects.filter(
            book_copy__book=book,
            borrowed_on=today
        ).count()

        BookUsageStat.objects.update_or_create(
            book=book,
            institution=book.institution,
            date=today,
            defaults={
                'borrow_count': borrow_count,
                'search_count': 0,  # TODO: integrate real search tracking logic
                'recommendation_score': calculate_recommendation_score(book),
                'average_rating': get_average_rating(book),
                'unique_borrowers_count': BorrowTransaction.objects.filter(
                    book_copy__book=book,
                    borrowed_on=today
                ).values('user').distinct().count()
            }
        )


def calculate_recommendation_score(book):
    """
    Estimate book popularity score based on borrowing, rating, and issue count.
    """
    borrow_total = BorrowTransaction.objects.filter(book_copy__book=book).count()
    avg_rating = get_average_rating(book)
    issue_count = BookIssueReport.objects.filter(book_copy__book=book).count()

    score = (borrow_total * 2) + (avg_rating * 5) - (issue_count * 1.5)
    return max(0.0, round(score, 2))


def get_average_rating(book):
    return BookRating.objects.filter(book=book).aggregate(avg=Avg('rating'))['avg'] or 0


@shared_task
def notify_damaged_or_lost_books():
    """
    Notifies assigned librarians/admins of unresolved damage or loss reports.
    """
    unresolved_issues = BookIssueReport.objects.filter(resolved=False).select_related(
        'book_copy__book', 'reported_by', 'assigned_to'
    )

    for issue in unresolved_issues:
        recipients = [issue.assigned_to] if issue.assigned_to else [issue.reported_by]
        for recipient in recipients:
            if recipient:
                send_notification(
                    user=recipient,
                    title="🚨 Unresolved Book Issue",
                    message=f"{issue.book_copy.book.title} "
                            f"({issue.book_copy.accession_number}) reported as '{issue.issue_type}' "
                            f"by {issue.reported_by.username}.",
                    target="library"
                )


@shared_task
def alert_membership_expiry(days_notice=7):
    """
    Notifies members if their library membership is expiring within `days_notice`.
    """
    target_date = timezone.now().date() + timedelta(days=days_notice)
    expiring_members = LibraryMember.objects.filter(
        is_active=True,
        membership_expiry__range=[timezone.now().date(), target_date]
    ).select_related('user')

    for member in expiring_members:
        send_notification(
            user=member.user,
            title="📅 Membership Expiry Reminder",
            message=f"Your library membership is set to expire on {member.membership_expiry}. "
                    f"Please renew it in time to continue enjoying services.",
            target="library"
        )
