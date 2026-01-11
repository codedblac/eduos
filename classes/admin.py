from django.contrib import admin
from django.db.models import Count, Q

from .models import (
    ClassLevel,
    Stream,
    StudentStreamEnrollment,
)


# ======================================================
# 🏫 CLASS LEVEL ADMIN
# ======================================================
@admin.register(ClassLevel)
class ClassLevelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "institution",
        "order",
        "is_graduating_level",
        "requires_national_exam",
        "class_teacher",
        "default_promotion_class",
    )

    list_filter = (
        "institution",
        "is_graduating_level",
        "requires_national_exam",
    )

    search_fields = (
        "name",
        "code",
        "institution__name",
        "class_teacher__user__first_name",
        "class_teacher__user__last_name",
    )

    ordering = ("institution__name", "order", "name")

    readonly_fields = ("created_at", "updated_at")

    autocomplete_fields = (
        "institution",
        "default_promotion_class",
        "class_teacher",
        "created_by",
        "updated_by",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "institution",
                    "name",
                    "code",
                    "order",
                    "description",
                    "is_graduating_level",
                    "requires_national_exam",
                    "class_teacher",
                    "default_promotion_class",
                )
            },
        ),
        (
            "Audit Info",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )


# ======================================================
# 🧑‍🏫 STREAM ADMIN
# ======================================================
@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "class_level",
        "institution",
        "academic_year",
        "stream_teacher",
        "capacity",
        "current_student_count_display",
        "is_over_capacity_display",
        "is_active",
    )

    list_filter = (
        "academic_year",
        "class_level__institution",
        "class_level",
        "is_active",
        "auto_promote_enabled",
    )

    search_fields = (
        "name",
        "code",
        "class_level__name",
        "class_level__institution__name",
        "academic_year__name",
        "stream_teacher__user__first_name",
        "stream_teacher__user__last_name",
    )

    ordering = (
        "academic_year",
        "class_level__order",
        "order",
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "current_student_count_display",
        "is_over_capacity_display",
    )

    autocomplete_fields = (
        "class_level",
        "academic_year",
        "stream_teacher",
        "created_by",
        "updated_by",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "code",
                    "order",
                    "description",
                    "class_level",
                    "academic_year",
                    "stream_teacher",
                    "capacity",
                    "is_active",
                    "auto_promote_enabled",
                )
            },
        ),
        (
            "Audit Info",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                    "current_student_count_display",
                    "is_over_capacity_display",
                ),
            },
        ),
    )

    # --------------------------------------------------
    # QUERY OPTIMIZATION
    # --------------------------------------------------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            "class_level",
            "academic_year",
            "stream_teacher",
            "class_level__institution",
        ).annotate(
            _active_students=Count(
                "enrollments_classes",
                filter=Q(enrollments_classes__status="active"),
                distinct=True,
            )
        )

    # --------------------------------------------------
    # ADMIN DISPLAY METHODS (REQUIRED)
    # --------------------------------------------------
    @admin.display(description="Institution", ordering="class_level__institution")
    def institution(self, obj):
        return obj.class_level.institution if obj.class_level else None

    @admin.display(description="Current Students")
    def current_student_count_display(self, obj):
        return getattr(obj, "_active_students", obj.current_student_count)

    @admin.display(boolean=True, description="Over Capacity")
    def is_over_capacity_display(self, obj):
        return obj.current_student_count > obj.capacity
