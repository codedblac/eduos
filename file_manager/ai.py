import os
import mimetypes
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from .models import ManagedFile
from accounts.models import CustomUser


class FileManagerAIEngine:
    """
    AI-powered automation and intelligence layer for the File Manager app.
    Supports tagging, content classification, relevance scoring, access suggestion, and future integrations.
    """

    def suggest_tags(self, file_name, content_type=None):
        """
        Suggest tags based on file name heuristics and content type.
        """
        tags = set()
        name_lower = file_name.lower()

        # Heuristic-based tagging
        if 'lesson' in name_lower:
            tags.add('lesson note')
        if 'exam' in name_lower:
            tags.add('exam')
        if 'homework' in name_lower or 'assignment' in name_lower:
            tags.add('homework')
        if 'report' in name_lower:
            tags.add('report')
        if 'ebook' in name_lower:
            tags.add('ebook')

        # MIME type-based tagging
        if content_type:
            if 'pdf' in content_type:
                tags.add('document')
            elif 'video' in content_type:
                tags.add('video')
            elif 'image' in content_type:
                tags.add('image')
            elif 'audio' in content_type:
                tags.add('audio')
            elif 'zip' in content_type:
                tags.add('archive')

        return list(tags)

    def auto_flag_sensitive(self, file: ManagedFile):
        """
        Detect if a file contains sensitive content (basic placeholder).
        To be enhanced with NLP/AI later.
        """
        flagged = False
        reason = ""

        tag_string = getattr(file, 'tags', '') or ''
        if any(keyword in tag_string.lower() for keyword in ['violence', 'explicit', 'hate']):
            flagged = True
            reason = "Sensitive content detected in tags."

        return flagged, reason

    def recommend_access(self, file: ManagedFile):
        """
        Suggest default access level based on category or metadata.
        """
        if file.is_public:
            return "public"
        if file.file_type in ['assignment', 'lesson_note']:
            return "class"
        if file.file_type == 'report':
            return "institution"
        return "private"

    def auto_expire_logic(self, file: ManagedFile):
        """
        Automatically set expiration for temporary/short-lived files.
        """
        if file.file_type in ['assignment', 'lesson_note']:
            return timezone.now() + timedelta(days=30)
        return None

    def auto_summary(self, file_path):
        """
        Placeholder for AI-generated file summaries.
        Future integration: NLP pipelines, transformers, etc.
        """
        return "Summary functionality will be available in future versions."

    def recommend_ai_features(self, user: CustomUser):
        """
        Suggest AI features based on the user role.
        """
        if user.is_superuser:
            return ["Smart Tagging", "Auto Expiry", "Content Summary", "Access Recommendation"]
        if getattr(user, 'is_teacher', False):
            return ["Tag Suggestions", "Bulk AI Tagging", "Auto Expiry"]
        if getattr(user, 'is_student', False):
            return ["Submission Check", "AI-generated Summaries"]
        if getattr(user, 'is_parent', False):
            return ["Track File Usage", "Summary Access"]
        return ["Basic Smart Tagging"]
