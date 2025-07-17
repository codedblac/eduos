from datetime import datetime, timedelta
from django.db.models import Count, F, Q, Avg
from .models import (
    Book, BookCopy, BorrowTransaction, BookRating,
    BookUsageStat, LibraryMember, Institution
)
from accounts.models import CustomUser


class LibraryAI:

    @staticmethod
    def top_borrowed_books(institution_id=None, limit=10):
        qs = Book.objects.all()
        if institution_id:
            qs = qs.filter(institution_id=institution_id)
        return qs.annotate(
            borrow_count=Count('copies__borrowtransaction')
        ).order_by('-borrow_count')[:limit]

    @staticmethod
    def overdue_statistics(institution_id=None):
        today = datetime.today().date()
        qs = BorrowTransaction.objects.filter(
            returned_on__isnull=True,
            due_date__lt=today
        )
        if institution_id:
            qs = qs.filter(book_copy__book__institution_id=institution_id)

        total_overdue = qs.count()
        overdue_by_user = qs.values('user__username').annotate(count=Count('id')).order_by('-count')
        return {
            'total_overdue': total_overdue,
            'overdue_by_user': list(overdue_by_user)
        }

    @staticmethod
    def user_borrowing_behavior(user_id):
        records = BorrowTransaction.objects.filter(user_id=user_id)
        total_borrowed = records.count()
        late_returns = records.filter(returned_on__gt=F('due_date')).count()
        most_borrowed = records.values('book_copy__book__title').annotate(count=Count('id')).order_by('-count')[:3]
        return {
            'total_borrowed': total_borrowed,
            'late_returns': late_returns,
            'most_borrowed_books': list(most_borrowed)
        }

    @staticmethod
    def subject_popularity_estimation(subjects):
        usage = {}
        for subject in subjects:
            books = Book.objects.filter(title__icontains=subject)  # Adjust subject linkage if you add subject FK
            borrow_count = BorrowTransaction.objects.filter(book_copy__book__in=books).count()
            usage[subject] = borrow_count
        return usage

    @staticmethod
    def damaged_books_summary(institution_id=None):
        qs = BookCopy.objects.filter(is_damaged=True)
        if institution_id:
            qs = qs.filter(book__institution_id=institution_id)
        return qs.count()

    @staticmethod
    def most_popular_authors(institution_id=None, limit=5):
        qs = Book.objects.all()
        if institution_id:
            qs = qs.filter(institution_id=institution_id)
        return qs.values('author').annotate(
            borrow_count=Count('copies__borrowtransaction')
        ).order_by('-borrow_count')[:limit]

    @staticmethod
    def least_used_books(threshold_days=90, institution_id=None):
        threshold_date = datetime.today().date() - timedelta(days=threshold_days)
        qs = Book.objects.all()
        if institution_id:
            qs = qs.filter(institution_id=institution_id)
        return qs.exclude(
            copies__borrowtransaction__borrowed_on__gte=threshold_date
        ).distinct()

    @staticmethod
    def top_frequent_borrowers(institution_id=None, limit=5):
        qs = BorrowTransaction.objects.all()
        if institution_id:
            qs = qs.filter(user__librarymember__institution_id=institution_id)
        return qs.values('user__username').annotate(
            total_borrowed=Count('id')
        ).order_by('-total_borrowed')[:limit]

    @staticmethod
    def borrowing_trend_by_month(institution_id=None):
        qs = BorrowTransaction.objects.all()
        if institution_id:
            qs = qs.filter(book_copy__book__institution_id=institution_id)
        return qs.annotate(
            month=F('borrowed_on__month'),
            year=F('borrowed_on__year')
        ).values('year', 'month').annotate(
            total=Count('id')
        ).order_by('year', 'month')

    @staticmethod
    def average_book_ratings(institution_id=None):
        qs = BookRating.objects.all()
        if institution_id:
            qs = qs.filter(institution_id=institution_id)
        return qs.values('book__title').annotate(
            average_rating=Avg('rating')
        ).order_by('-average_rating')[:10]

    @staticmethod
    def ai_recommendations_for_user(user_id, institution_id=None, limit=5):
        """ Very basic placeholder AI logic: recommend top-rated books not yet borrowed by the user """
        borrowed_books = BorrowTransaction.objects.filter(user_id=user_id).values_list('book_copy__book_id', flat=True)

        qs = Book.objects.exclude(id__in=borrowed_books)
        if institution_id:
            qs = qs.filter(institution_id=institution_id)

        return qs.annotate(
            avg_rating=Avg('ratings__rating')
        ).order_by('-avg_rating')[:limit]

