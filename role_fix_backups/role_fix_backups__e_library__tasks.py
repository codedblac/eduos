from celery import shared_task
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta

from .models import ELibraryResource, ResourceViewLog
from notifications.utils import send_notification
from accounts.models import CustomUser

from .ai import ELibraryAIEngine


@shared_task
def auto_generate_summaries_and_tags():
    """
    Runs through unprocessed resources to generate AI summaries and tags.
    Intended to be run hourly or nightly via Celery Beat.
    """
    resources = ELibraryResource.objects.filter(
        auto_summary__isnull=True,
        file__isnull=False,
        is_approved=True
    )

    for resource in resources:
        try:
            summary = ELibraryAIEngine.generate_content_summary(resource)
            tags = ELibraryAIEngine.detect_content_topics(resource)

            resource.auto_summary = summary
            resource.ai_tags = ', '.join(tags) if isinstance(tags, list) else str(tags)
            resource.save(update_fields=["auto_summary", "ai_tags", "updated_at"])
        except Exception as e:
            print(f"[e_library AI] Failed to process {resource.title}: {e}")


@shared_task
def track_popular_resources():
    """
    Update trending/popular resource metadata for analytics or frontend use.
    Example: mark top N resources by view count weekly.
    """
    trending = ELibraryResource.objects.annotate(
        views_last_7_days=Count('views', filter=timezone.now() - timedelta(days=7) <= timezone.now())
    ).order_by('-views_last_7_days')[:10]

    for resource in trending:
        # Optionally notify uploader
        send_notification(
            user=resource.uploader,
            title="Trending Resource!",
            message=f"Your resource '{resource.title}' is among the top viewed this week!",
            target="e_library"
        )


@shared_task
def cleanup_unapproved_resources(threshold_days=30):
    """
    Deletes or flags resources that are not approved within X days.
    """
    threshold_date = timezone.now() - timedelta(days=threshold_days)
    old_unapproved = ELibraryResource.objects.filter(
        is_approved=False,
        created_at__lt=threshold_date
    )

    count = old_unapproved.count()
    old_unapproved.delete()
    print(f"[e_library cleanup] Deleted {count} unapproved old resources.")


@shared_task
def weekly_usage_report():
    """
    Send weekly usage summary to institution admins.
    Could be extended to attach downloadable reports.
    """
    institutions = ELibraryResource.objects.values_list('institution', flat=True).distinct()

    for institution_id in institutions:
        resource_count = ELibraryResource.objects.filter(institution_id=institution_id).count()
        view_count = ResourceViewLog.objects.filter(resource__institution_id=institution_id).count()

        admins = CustomUser.objects.filter(profile__institution_id=institution_id, profile__role__in=["admin", "super_admin"])
        for admin in admins:
            send_notification(
                user=admin,
                title="Weekly e-Library Report",
                message=f"You currently have {resource_count} resources with {view_count} total views.",
                target="e_library"
            )
