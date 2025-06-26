from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ManagedFileViewSet,
    FileAccessLogViewSet,
    AssignmentSubmissionViewSet,
    PublicFileListView,
    MyUploadsView,
    RestoreFromTrashView,
    ExpiredFileCleanupView,
    FileDownloadView,
)

router = DefaultRouter()
router.register(r'files', ManagedFileViewSet, basename='managedfile')
router.register(r'access-logs', FileAccessLogViewSet, basename='fileaccesslog')
router.register(r'submissions', AssignmentSubmissionViewSet, basename='assignmentsubmission')

urlpatterns = [
    path('', include(router.urls)),

    # Extra utility views
    path('public/', PublicFileListView.as_view(), name='public-files'),
    path('my-uploads/', MyUploadsView.as_view(), name='my-uploads'),
    path('trash/restore/<int:pk>/', RestoreFromTrashView.as_view(), name='restore-from-trash'),
    path('expired/', ExpiredFileCleanupView.as_view(), name='expired-file-cleanup'),
    path('download/<int:pk>/', FileDownloadView.as_view(), name='file-download'),
]
