# Generated by Django 3.2.7 on 2022-01-18 07:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0010_auto_20220116_1354'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='files',
            new_name='attached_file',
        ),
    ]
