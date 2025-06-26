from django.db import models

# Create your models here.
# library/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from institutions.models import Institution

User = get_user_model()

# ========== Book Metadata ==========
class BookCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='books')
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True)
    publication_year = models.PositiveIntegerField(blank=True, null=True)
    edition = models.CharField(max_length=50, blank=True, null=True)
    language = models.CharField(max_length=50, default="English")
    category = models.ForeignKey(BookCategory, on_delete=models.SET_NULL, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

# ========== Accession & Inventory ==========
class BookCopy(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copies')
    accession_number = models.CharField(max_length=50, unique=True)
    is_available = models.BooleanField(default=True)
    is_damaged = models.BooleanField(default=False)
    is_lost = models.BooleanField(default=False)
    location = models.CharField(max_length=255, help_text="Shelf or physical location")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.book.title} - {self.accession_number}"

# ========== Borrowing System ==========
class BorrowTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrowed_books')
    book_copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE)
    borrowed_on = models.DateField(default=timezone.now)
    due_date = models.DateField()
    returned_on = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'book_copy', 'borrowed_on')

    @property
    def is_overdue(self):
        return not self.returned_on and timezone.now().date() > self.due_date

    def __str__(self):
        return f"{self.user} borrowed {self.book_copy.accession_number}"

class LibraryMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    membership_type = models.CharField(max_length=50, choices=[
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('staff', 'Staff'),
        ('external', 'External Member')
    ])
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.membership_type}"


class Fine(models.Model):
    transaction = models.OneToOneField(BorrowTransaction, on_delete=models.CASCADE, related_name='fine')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    paid = models.BooleanField(default=False)
    paid_on = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Fine for {self.transaction}"

# ========== Procurement & Acquisition ==========
class Vendor(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Acquisition(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    acquisition_date = models.DateField(default=timezone.now)
    funding_source = models.CharField(max_length=255, blank=True, null=True)

    def total_cost(self):
        return self.quantity * self.price_per_unit

    def __str__(self):
        return f"{self.book.title} - {self.quantity} copies"

# ========== Damage, Repair & Loss ==========
class BookIssueReport(models.Model):
    book_copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE, related_name='issues')
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    issue_type = models.CharField(max_length=50, choices=[
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
        ('repair', 'Needs Repair'),
    ])
    description = models.TextField()
    reported_on = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_on = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Issue - {self.issue_type} - {self.book_copy.accession_number}"

# ========== Feedback & Ratings ==========
class BookRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveSmallIntegerField(default=5)
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.book.title} rated {self.rating}"

# ========== AI & Analytics ==========
class BookUsageStat(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='usage_stats')
    date = models.DateField()
    borrow_count = models.PositiveIntegerField(default=0)
    search_count = models.PositiveIntegerField(default=0)
    recommendation_score = models.FloatField(default=0.0, help_text="AI-generated score for popularity or relevance")

    class Meta:
        unique_together = ('book', 'date')

    def __str__(self):
        return f"Stats for {self.book.title} on {self.date}"
