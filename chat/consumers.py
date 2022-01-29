import json
from django.http.request import HttpRequest
from chat.models import Chat, Message
from .serializers import MessageSerializer
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from django.db.models import Count, Q

User = get_user_model()


class ChatConsumer(WebsocketConsumer):

    ROOM_NAME = None
    MESSAGE_QUEUE = []

    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.ROOM_NAME, self.channel_name
        )
        self.ROOM_NAME = None

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        command = data["command"]
        self.commands[command](self, data)

    def set_group(self, data):
        chat_type = data["chatType"]
        if chat_type == "PB":
            roomName = data["roomName"]
            room = Chat.objects.get(name=roomName)
            if room:
                self.CHAT_ID = room.id
                self.ROOM_NAME = f'{room.name.split(" ")[0]}_{room.id}'
                async_to_sync(self.channel_layer.group_add)(
                    self.ROOM_NAME, self.channel_name
                )

        elif chat_type == "PR":
            username = data["username"]
            contactname = data["contact"]
            user = User.objects.get(username=username)
            contact = User.objects.get(username=contactname)

            room = (
                Chat.objects.annotate(
                    total_members=Count("members"),
                    matching_members=Count(
                        "members", filter=Q(members__in=[user, contact])
                    ),
                )
                .filter(matching_members=2, total_members=2)
                .filter(chat_type=chat_type)
            )
            if room:
                room = room[0]
                self.CHAT_ID = room.id
                self.ROOM_NAME = f'{room.name.split(" ")[0]}_{room.id}'
                async_to_sync(self.channel_layer.group_add)(
                    self.ROOM_NAME, self.channel_name
                )
            else:
                print("Room not found please handle the error")
        else:
            pass

    def create_message(self, data):
        username = data["author"]
        message = data["message"]
        user = User.objects.get(username=username)

        chat = Chat.objects.get(id=self.CHAT_ID)

        created_message = Message.objects.create(
            chat=chat, author=user, content=message
        )
        created_message.read_by.add(user)
        request = HttpRequest()
        request.build_absolute_uri = (
            lambda location: f'http://{self.scope["headers"][0][1].decode()}{location}'
        )
        serializer = MessageSerializer(
            created_message, many=False, context={"request": request}
        )
        return serializer.data

    def new_message(self, data):
        try:
            if self.CHAT_ID:
                if self.MESSAGE_QUEUE.__len__() > 0:
                    message = self.create_message(self.MESSAGE_QUEUE[0])
                    async_to_sync(self.channel_layer.group_send)(
                        self.ROOM_NAME, {"type": "send_message", "message": message}
                    )
                    self.MESSAGE_QUEUE.pop()
                message = self.create_message(data)
                async_to_sync(self.channel_layer.group_send)(
                    self.ROOM_NAME, {"type": "send_message", "message": message}
                )

        except AttributeError:
            self.MESSAGE_QUEUE.append(data)
            self.send(text_data=json.dumps({"reInitialize": True}))

    def mark_message_as_read(self, data):
        username = data["username"]
        room_id = data["room_id"]
        last_message_id = data["last_message"]
        user = User.objects.get(username=username)
        room = Chat.objects.get(id=room_id)
        message = Message.objects.get(id=last_message_id)
        unread_messages = Message.objects.filter(
            chat=room, timestamp__lt=message.timestamp
        ).exclude(read_by__in=[user])
        if unread_messages.count() > 0:
            for msg in unread_messages:
                msg.read_by.add(user)

    def echo_message(self, data):
        async_to_sync(self.channel_layer.group_send)(
            self.ROOM_NAME, {"type": "send_message", "message": data["message"]}
        )

    commands = {
        "newMessage": new_message,
        "goToRoom": set_group,
        "markAsRead": mark_message_as_read,
        "sendMessage": echo_message,
    }

    def send_message(self, event):
        message = event["message"]

        self.send(text_data=json.dumps({"message": message}))
