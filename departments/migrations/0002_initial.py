# Generated by Django 5.2.1 on 2025-07-17 14:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('academics', '0002_initial'),
        ('classes', '0001_initial'),
        ('departments', '0001_initial'),
        ('students', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='departmentperformancenote',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.student'),
        ),
        migrations.AddField(
            model_name='departmentperformancenote',
            name='term',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='academics.term'),
        ),
        migrations.AddField(
            model_name='departmentresource',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='departments.department'),
        ),
        migrations.AddField(
            model_name='departmentroleassignmenthistory',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='departments.department'),
        ),
        migrations.AddField(
            model_name='departmentroleassignmenthistory',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='departmenttask',
            name='assigned_to',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='departmenttask',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='departments.department'),
        ),
        migrations.AddField(
            model_name='departmentuser',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='departments.department'),
        ),
        migrations.AddField(
            model_name='departmentuser',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='subject',
            name='assigned_teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_subjects', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='subject',
            name='class_levels',
            field=models.ManyToManyField(blank=True, related_name='subjects', to='classes.classlevel'),
        ),
        migrations.AddField(
            model_name='subject',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='departments.department'),
        ),
        migrations.AlterUniqueTogether(
            name='department',
            unique_together={('name', 'institution')},
        ),
        migrations.AlterUniqueTogether(
            name='departmentuser',
            unique_together={('user', 'department')},
        ),
        migrations.AlterUniqueTogether(
            name='subject',
            unique_together={('name', 'department')},
        ),
    ]
