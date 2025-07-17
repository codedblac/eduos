from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    BookViewSet,
    BookCopyViewSet,
    BorrowTransactionViewSet,
    LibraryMemberViewSet,
    AcquisitionViewSet,
    BookRatingViewSet,
    BookRequestViewSet,
    BookRecommendationViewSet,
)

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'book-copies', BookCopyViewSet, basename='book-copy')
router.register(r'borrow-transactions', BorrowTransactionViewSet, basename='borrow-transaction')
router.register(r'members', LibraryMemberViewSet, basename='library-member')
router.register(r'acquisitions', AcquisitionViewSet, basename='acquisition')
router.register(r'ratings', BookRatingViewSet, basename='book-rating')
router.register(r'requests', BookRequestViewSet, basename='book-request')
router.register(r'recommendations', BookRecommendationViewSet, basename='book-recommendation')

urlpatterns = [
    path('', include(router.urls)),
]
