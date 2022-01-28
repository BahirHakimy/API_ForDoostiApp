from django.contrib import admin
from .models import Chat, Message


class ChatAdmin(admin.ModelAdmin):
    list_display = ("name", "chat_type", "date_created")
    list_filter = ("chat_type",)
    list_search = ("name", "chat_type")


class MessageAdmin(admin.ModelAdmin):
    list_display = ("author", "content", "timestamp")
    list_filter = ("chat", "author")
    list_search = ("author", "content")


admin.site.register(Chat, ChatAdmin)
admin.site.register(Message, MessageAdmin)
