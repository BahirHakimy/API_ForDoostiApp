from django.contrib.auth import get_user_model
from rest_framework import serializers

from dosti.serializers import FriendDataSerializer
from .models import Chat, Message

User = get_user_model()


class UserSerailizer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField("get_fullname")

    class Meta:
        model = User
        fields = ("username", "fullname")

    def get_fullname(self, object):
        return f"{object.first_name} {object.last_name}"


class ChatSerializer(serializers.ModelSerializer):

    members = UserSerailizer(read_only=True, many=True)

    class Meta:
        model = Chat
        fields = ("name", "chat_type", "members", "date_created")

    def get_unread_messages(self, object):
        return Message.objects.filter(chat=object, read=False).count()


class MessageSerializer(serializers.ModelSerializer):

    author = FriendDataSerializer(read_only=True, many=False)
    attached_file = serializers.FileField()

    class Meta:
        model = Message
        fields = ("id", "author", "content", "attached_file", "timestamp")
