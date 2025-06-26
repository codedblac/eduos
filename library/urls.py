from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BookViewSet,
    BookCopyViewSet,
    BookBorrowRecordViewSet,
    LibraryMemberViewSet,
    LibrarySupplierViewSet,
    LibraryAcquisitionViewSet,
    LibraryAIInsightsAPIView,
)

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'book-copies', BookCopyViewSet, basename='bookcopy')
router.register(r'borrow-records', BookBorrowRecordViewSet, basename='borrowrecord')
router.register(r'members', LibraryMemberViewSet, basename='member')
router.register(r'suppliers', LibrarySupplierViewSet, basename='supplier')
router.register(r'acquisitions', LibraryAcquisitionViewSet, basename='acquisition')

urlpatterns = [
    # REST API endpoints for CRUD operations
    path('', include(router.urls)),

    # AI-powered analytics endpoint
    path('ai-insights/', LibraryAIInsightsAPIView.as_view(), name='library-ai-insights'),
]
