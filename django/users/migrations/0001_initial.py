# Generated by Django 5.0.6 on 2024-05-28 08:05

import users.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('is_staff', models.BooleanField(default=False, verbose_name='운영진')),
                ('is_down', models.BooleanField(default=False, verbose_name='휴면회원')),
                ('is_active', models.BooleanField(default=True, verbose_name='활동회원')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='가입일자')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일자')),
                ('login_method', models.CharField(default='kakao', max_length=20)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'Users',
            },
            managers=[
                ('objects', users.models.UserManager()),
            ],
        ),
    ]