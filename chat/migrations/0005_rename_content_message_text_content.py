# Generated by Django 3.2.7 on 2021-12-29 08:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_alter_chat_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='content',
            new_name='text_content',
        ),
    ]
