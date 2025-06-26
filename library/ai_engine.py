# library/ai.py
from django.db.models import Count, Q, F

from datetime import datetime, timedelta
from collections import Counter
from django.db.models import Count, Q
from .models import Book, BookBorrowRecord
from students.models import Student
from accounts.models import CustomUser

class LibraryAI:

    @staticmethod
    def top_borrowed_books(limit=10):
        return Book.objects.annotate(borrow_count=Count('borrow_records')).order_by('-borrow_count')[:limit]

    @staticmethod
    def overdue_statistics():
        today = datetime.today().date()
        overdue_records = BookBorrowRecord.objects.filter(
            return_date__isnull=True,
            due_date__lt=today
        )
        total_overdue = overdue_records.count()
        by_class = overdue_records.values('student__current_class').annotate(count=Count('id'))
        return {
            'total_overdue': total_overdue,
            'overdue_by_class': list(by_class)
        }

    @staticmethod
    def student_borrowing_behavior(student_id):
        records = BookBorrowRecord.objects.filter(student_id=student_id)
        total_borrowed = records.count()
        late_returns = records.filter(return_date__gt=F('due_date')).count()
        most_borrowed = records.values('book__title').annotate(count=Count('id')).order_by('-count')[:3]
        return {
            'total_borrowed': total_borrowed,
            'late_returns': late_returns,
            'most_borrowed_books': list(most_borrowed)
        }

    @staticmethod
    def usage_vs_syllabus_mapping():
        # Example placeholder logic
        subjects = ['Math', 'English', 'Biology', 'History']
        usage = {}
        for subject in subjects:
            count = Book.objects.filter(subject__icontains=subject).annotate(
                borrow_count=Count('borrow_records')
            ).aggregate(total=Count('borrow_records'))['total'] or 0
            usage[subject] = count
        return usage

    @staticmethod
    def damaged_books_analysis():
        return Book.objects.filter(condition='damaged').count()

    @staticmethod
    def popular_authors(limit=5):
        return Book.objects.values('author').annotate(
            count=Count('borrow_records')
        ).order_by('-count')[:limit]

    @staticmethod
    def inactive_books(threshold_days=90):
        threshold_date = datetime.today() - timedelta(days=threshold_days)
        return Book.objects.exclude(
            borrow_records__borrow_date__gte=threshold_date
        )

    @staticmethod
    def frequent_borrowers(limit=5):
        return Student.objects.annotate(
            borrow_count=Count('borrow_records')
        ).order_by('-borrow_count')[:limit]

    @staticmethod
    def borrowing_trends_by_term():
        return BookBorrowRecord.objects.annotate(
            term=F('term')
        ).values('term').annotate(
            total=Count('id')
        ).order_by('term')

