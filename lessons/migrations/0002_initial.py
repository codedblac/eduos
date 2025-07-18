# Generated by Django 5.2.1 on 2025-07-17 14:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('academics', '0002_initial'),
        ('institutions', '0001_initial'),
        ('lessons', '0001_initial'),
        ('subjects', '0001_initial'),
        ('syllabus', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='lessonplan',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subjects.subject'),
        ),
        migrations.AddField(
            model_name='lessonplan',
            name='subtopic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='syllabus.syllabussubtopic'),
        ),
        migrations.AddField(
            model_name='lessonplan',
            name='teacher',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='lessonplan',
            name='term',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academics.term'),
        ),
        migrations.AddField(
            model_name='lessonplan',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='syllabus.syllabustopic'),
        ),
        migrations.AddField(
            model_name='lessonscaffoldsuggestion',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='lessonscaffoldsuggestion',
            name='lesson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scaffold_suggestions', to='lessons.lessonplan'),
        ),
        migrations.AddField(
            model_name='lessonschedule',
            name='lesson_plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='lessons.lessonplan'),
        ),
        migrations.AddField(
            model_name='lessonsession',
            name='lesson_schedule',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='session', to='lessons.lessonschedule'),
        ),
        migrations.AddField(
            model_name='lessonsession',
            name='recorded_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lesson_records', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='lessonsession',
            name='reviewed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='session_reviews', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='lessonfeedback',
            name='lesson_session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='lessons.lessonsession'),
        ),
        migrations.AddField(
            model_name='lessonattachment',
            name='lesson_session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='lessons.lessonsession'),
        ),
        migrations.AddField(
            model_name='lessontemplate',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='lessontemplate',
            name='institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='institutions.institution'),
        ),
        migrations.AddField(
            model_name='lessontemplate',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subjects.subject'),
        ),
        migrations.AddField(
            model_name='lessontemplate',
            name='subtopic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='syllabus.syllabussubtopic'),
        ),
        migrations.AddField(
            model_name='lessontemplate',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='syllabus.syllabustopic'),
        ),
        migrations.AlterUniqueTogether(
            name='lessonplan',
            unique_together={('term', 'subject', 'class_level', 'teacher', 'topic', 'week_number')},
        ),
    ]
