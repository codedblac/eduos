# myproject/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/institutions/', include('institutions.urls')),
    path('api/v1/teachers/', include('teachers.urls')),
    path('api/v1/classes/', include('classes.urls')),
    path('api/v1/subjects/', include('subjects.urls')),
    path('api/v1/timetable/', include('timetable.urls')),
    path('api/v1/exams/', include('exams.urls')),
    path('api/v1/students/', include('students.urls')),
    path('api/v1/medical/', include('medical.urls')),
    path('api/v1/library/', include('library.urls')),
    path('api/v1/e-library/', include('e_library.urls')),
    path('api/v1/guardians/', include('guardians.urls')),
    path('api/v1/finance/', include('finance.urls')),
    path('api/v1/notifications/', include('notifications.urls')),
    path('api/v1/attendance/', include('attendance.urls')),
    path('api/v1/discipline/', include('discipline.urls')),
    path('api/v1/reports/', include('reports.urls')),
    path('api/v1/events/', include('events.urls')),
    path('api/v1/e-learning/', include('e_learning.urls')),
    path('api/v1/store-inventory/', include('store_inventory.urls')),
    path('api/v1/hostel/', include('hostel.urls')),
    path('api/v1/transport/', include('transport.urls')),
    path('api/v1/alumni/', include('alumni.urls')),
    path('api/v1/maintenance/', include('maintenance.urls')),
    path('api/v1/front-office/', include('front_office.urls')),
    path('api/v1/departments/', include('departments.urls')),
    path('api/v1/staff/', include('staff.urls')),
    path('api/v1/payroll/', include('payroll.urls')),
    path('api/v1/hrm/', include('hrm.urls')),
    path('api/v1/procurement/', include('procurement.urls')),
    path('api/v1/syllabus/', include('syllabus.urls')),
    path('api/v1/academics/', include('academics.urls')),
    path('api/v1/lessons/', include('lessons.urls')),
    path('api/v1/assessments/', include('assessments.urls')),
    path('api/v1/co-curricular/', include('co_curricular.urls')),
    path('api/v1/admissions/', include('admissions.urls')),
    path('api/v1/id-cards/', include('id_cards.urls')),
    path('api/v1/chat/', include('chat.urls')),
    path('api/v1/communication/', include('communication.urls')),
    path('api/v1/file-manager/', include('file_manager.urls')),
    path('api/v1/fee-management/', include('fee_management.urls')),
    path('api/v1/e-wallet/', include('e_wallet.urls')),
    path('api/v1/access-control/', include('access_control.urls')),
    path('', include('landing.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
