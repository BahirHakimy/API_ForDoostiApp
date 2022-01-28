# Generated by Django 3.2.3 on 2021-08-12 18:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dosti', '0003_alter_userprofilemodel_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friendship',
            name='friends',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='friend_list', to=settings.AUTH_USER_MODEL),
        ),
    ]
