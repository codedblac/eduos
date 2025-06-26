# myproject/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/institutions/', include('institutions.urls' )),
    path('api/teachers/', include('teachers.urls' )),
    path('api/classes/', include('classes.urls')),
    path('api/timetable/', include('timetable.urls')),
    path('api/subjects/', include('subjects.urls')),
    path('api/exams/', include('exams.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
