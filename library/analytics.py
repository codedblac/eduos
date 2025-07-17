from django.db.models import Count, Avg, Sum, Q, F
from datetime import datetime, timedelta
from .models import (
    Book, BookCopy, BorrowTransaction, Fine,
    Acquisition, Vendor, LibraryMember, BookRating, BookUsageStat
)


class LibraryAnalyticsEngine:

    def __init__(self, institution):
        self.institution = institution

    def book_inventory_summary(self):
        books = Book.objects.filter(institution=self.institution)
        total_books = books.count()
        total_copies = BookCopy.objects.filter(book__institution=self.institution).count()
        available_copies = BookCopy.objects.filter(
            book__institution=self.institution, is_available=True, is_damaged=False, is_lost=False
        ).count()
        damaged_copies = BookCopy.objects.filter(book__institution=self.institution, is_damaged=True).count()
        lost_copies = BookCopy.objects.filter(book__institution=self.institution, is_lost=True).count()

        return {
            "total_books": total_books,
            "total_copies": total_copies,
            "available_copies": available_copies,
            "damaged_copies": damaged_copies,
            "lost_copies": lost_copies
        }

    def borrowing_statistics(self):
        transactions = BorrowTransaction.objects.filter(book_copy__book__institution=self.institution)
        active_borrows = transactions.filter(returned_on__isnull=True).count()
        returned_borrows = transactions.filter(returned_on__isnull=False).count()
        overdue_borrows = transactions.filter(returned_on__isnull=True, due_date__lt=datetime.today().date()).count()

        return {
            "active_borrows": active_borrows,
            "returned_borrows": returned_borrows,
            "overdue_borrows": overdue_borrows
        }

    def fine_statistics(self):
        fines = Fine.objects.filter(institution=self.institution)
        total_fines = fines.aggregate(total=Sum('amount'))['total'] or 0
        paid_fines = fines.filter(paid=True).aggregate(paid=Sum('amount'))['paid'] or 0
        unpaid_fines = total_fines - paid_fines
        waived_fines = fines.filter(waived=True).aggregate(waived=Sum('amount'))['waived'] or 0

        return {
            "total_fines": float(total_fines),
            "paid_fines": float(paid_fines),
            "unpaid_fines": float(unpaid_fines),
            "waived_fines": float(waived_fines)
        }

    def acquisition_summary(self):
        acquisitions = Acquisition.objects.filter(book__institution=self.institution)
        total_spent = acquisitions.aggregate(cost=Sum(F('price_per_unit') * F('quantity')))['cost'] or 0
        vendors = Vendor.objects.filter(acquisition__book__institution=self.institution).distinct().count()
        books_procured = acquisitions.values('book').distinct().count()

        return {
            "total_spent": float(total_spent),
            "vendor_count": vendors,
            "books_procured": books_procured
        }

    def member_statistics(self):
        members = LibraryMember.objects.filter(institution=self.institution)
        total_members = members.count()
        active_members = members.filter(is_active=True).count()
        inactive_members = total_members - active_members
        roles = members.values('membership_type').annotate(count=Count('id'))

        return {
            "total_members": total_members,
            "active_members": active_members,
            "inactive_members": inactive_members,
            "roles_breakdown": list(roles)
        }

    def rating_summary(self):
        ratings = BookRating.objects.filter(institution=self.institution)
        total_ratings = ratings.count()
        avg_rating = ratings.aggregate(avg=Avg('rating'))['avg'] or 0

        top_rated_books = ratings.values('book__title').annotate(
            average=Avg('rating'),
            count=Count('id')
        ).order_by('-average')[:5]

        return {
            "total_ratings": total_ratings,
            "average_rating": round(avg_rating, 2),
            "top_rated_books": list(top_rated_books)
        }

    def usage_summary(self):
        stats = BookUsageStat.objects.filter(institution=self.institution)
        total_searches = stats.aggregate(searches=Sum('search_count'))['searches'] or 0
        total_borrows = stats.aggregate(borrows=Sum('borrow_count'))['borrows'] or 0

        return {
            "total_searches": total_searches,
            "total_borrows": total_borrows
        }

    def full_report(self):
        return {
            "inventory": self.book_inventory_summary(),
            "borrowing": self.borrowing_statistics(),
            "fines": self.fine_statistics(),
            "acquisition": self.acquisition_summary(),
            "members": self.member_statistics(),
            "ratings": self.rating_summary(),
            "usage": self.usage_summary()
        }
