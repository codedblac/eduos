# Generated by Django 5.2.1 on 2025-07-17 14:35

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Institution',
                'verbose_name_plural': 'Institutions',
            },
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(max_length=150)),
                ('last_name', models.CharField(max_length=150)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('role', models.CharField(choices=[('SUPER_ADMIN', 'Super Admin'), ('ADMIN', 'School Admin'), ('TEACHER', 'Teacher'), ('STUDENT', 'Student'), ('LIBRARIAN', 'Librarian'), ('STORE_KEEPER', 'Store Keeper'), ('BURSAR', 'Bursar'), ('HOSTEL_MANAGER', 'Hostel Manager'), ('FINANCE', 'Finance Officer'), ('SUPPORT_STAFF', 'Support Staff'), ('PUBLIC_LEARNER', 'Public Learner'), ('PUBLIC_TEACHER', 'Public Teacher'), ('GOV_USER', 'Government User')], max_length=30)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='user_avatars/')),
                ('reset_token', models.CharField(blank=True, max_length=64, null=True)),
                ('reset_token_expiry', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('last_login_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('last_user_agent', models.TextField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('institution', models.ForeignKey(blank=True, help_text='Only institutional users have this set. Public and GOV users have it null.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.institution')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
        ),
    ]
