import base64
import datetime
from django.core.files.base import ContentFile
from copy import Error
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from dosti.serializers import (
    FriendDataSerializer,
    UserSearchProfileSerializer,
)
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer
from dosti.models import Friendship, UserProfile
from django.db.models import Q, Count
from django.db.utils import IntegrityError

User = get_user_model()


@api_view(["GET"])
def roomsListView(request):
    rooms = Chat.objects.filter(chat_type="PB").order_by("-date_created")
    if len(rooms) > 0:
        serializer = ChatSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(
            {"message": "No chat rooms availble"}, status=status.HTTP_200_OK
        )


@api_view(["POST"])
def roomsSearchView(request):
    serach = request.data["search"]
    rooms = Chat.objects.filter(name__contains=serach, chat_type="PB")
    if len(rooms) > 0:
        serializer = ChatSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"message": "No rooms found"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def createRoomView(request):
    username = request.data["username"]
    roomname = request.data["room"]
    user = User.objects.get(username=username)
    try:
        room = Chat.objects.create(name=roomname, chat_type="PB")
        room.members.add(user)
        room.save()
        return Response(
            {"message": "Room created successfully"}, status=status.HTTP_201_CREATED
        )
    except IntegrityError:
        return Response(
            {"message": "Room name is allready taken"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Error:
        return Response(
            {"message": "Some thing went wrong"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def getChat(request):

    chat_type = request.data["chatType"]

    if chat_type == "PB":
        username = request.data["username"]
        user = User.objects.get(username=username)
        roomname = request.data["roomName"]
        room = Chat.objects.get(name=roomname)
        if user not in room.members.all():
            room.members.add(user)
        messages = Message.objects.get_message_group(room=room)
        read_by_users = []
        for message in messages:
            if user in message.read_by.all():
                read_by_users.append(message.id)

        serializer = MessageSerializer(
            messages, context={"request": request}, many=True
        )
        conversation = serializer.data.copy()
        for message in conversation:
            if message["id"] in read_by_users:
                message["read"] = True
            else:
                message["read"] = False

        return Response(
            {
                "conversation": conversation,
                "contact_profile": {
                    "name": room.name,
                    "room_id": room.id,
                    "members": room.members.count(),
                },
            },
            status=status.HTTP_200_OK,
        )
    elif chat_type == "PR":
        username = request.data["username"]
        contact_name = request.data["contact"]
        user = User.objects.get(username=username)
        contact = User.objects.get(username=contact_name)
        contact_profile = UserProfile.objects.get(user=contact)
        contact_serializer = UserSearchProfileSerializer(
            contact_profile, many=False, context={"request": request}
        )

        members = [user, contact]
        room = (
            Chat.objects.annotate(
                total_members=Count("members"),
                matching_members=Count("members", filter=Q(members__in=members)),
            )
            .filter(matching_members=2, total_members=2)
            .filter(chat_type=chat_type)
        )
        if len(room) > 0:
            room = room[0]
            read_by_users = []
            messages = Message.objects.get_message_group(room=room)
            for message in messages:
                if user in message.read_by.all():
                    read_by_users.append(message.id)
            data = contact_serializer.data.copy()
            data["room_id"] = room.id
            if messages:
                serializer = MessageSerializer(
                    messages, context={"request": request}, many=True
                )
                conversation = serializer.data.copy()
                for message in conversation:
                    if message["id"] in read_by_users:
                        message["read"] = True
                    else:
                        message["read"] = False

                return Response(
                    {
                        "conversation": conversation,
                        "contact_profile": data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "conversation": [],
                        "contact_profile": data,
                    },
                    status=status.HTTP_200_OK,
                )

        else:

            room = Chat.objects.create(
                chat_type=chat_type, name=f"prv_chat{user.id}-{contact.id}"
            )
            room.members.add(user)
            room.members.add(contact)
            room.save()
            data = contact_serializer.data.copy()
            data["room_id"] = room.id
            return Response(
                {
                    "conversation": [],
                    "contact_profile": data,
                },
                status=status.HTTP_200_OK,
            )


@api_view(["POST"])
def load_messages(request):
    room_id = request.data["room_id"]
    lastmessage_id = request.data["lastmessage_id"]
    room = Chat.objects.get(id=room_id)
    messages = Message.objects.get_older_messages(room, lastmessage_id)
    message_serializer = MessageSerializer(
        messages, many=True, context={"request": request}
    )
    if messages:
        return Response(message_serializer.data, status=status.HTTP_200_OK)

    else:
        return Response([], status=status.HTTP_200_OK)


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def file_upload_endpoint(request):
    try:
        file_type = request.data["fileType"]
    except KeyError:
        file_type = None
    username = request.data["username"]
    room_id = request.data["room_id"]
    file = request.data["file"]
    user = User.objects.get(username=username)
    chat = Chat.objects.get(id=room_id)
    if file_type:
        file.name = f"{datetime.datetime.now()}{file_type}"

    message = Message.objects.create(
        chat=chat, author=user, content=f"file: {file.name}", attached_file=file
    )
    message.read_by.add(user)

    serializer = MessageSerializer(message, context={"request": request})

    return Response(serializer.data, status=status.HTTP_200_OK)


def get_recent_chats(request, username):
    """
    Returns the 5 recent chats of the User
    """
    chats = Chat.objects.filter(members__username=username)
    user = User.objects.get(username=username)

    # Get the last message of every chat that user is member on
    recent_chats = []
    for chat in chats:
        messages = Message.objects.filter(chat=chat).order_by("-timestamp")
        if messages.exists():
            recent_chats.append(messages[0].id)

    # Organize the messages within a group to be able to order them by timestamp and get the first 5
    messages = Message.objects.filter(id__in=recent_chats).order_by("-timestamp")[0:5]

    # Fetch the chat of each message
    chat_id_list = []
    for message in messages:
        chat_id_list.append(message.chat.id)
    new_chats = Chat.objects.filter(id__in=chat_id_list)

    # Organize the chats to public or private to be able to serializer them correctly
    privates = new_chats.filter(chat_type="PR")
    rooms = new_chats.filter(chat_type="PB")

    # Serializer the public chats and add unread messages count to each chatroom
    if len(rooms) > 0:
        unread_messages_count = []
        for room in rooms:
            unread_messages = (
                Message.objects.filter(chat=room).exclude(read_by__in=[user]).count()
            )
            unread_messages_count.append(unread_messages)
        chat_serializer = ChatSerializer(rooms, many=True)
        chat_serializer = chat_serializer.data.copy()
        counter = 0
        for room in chat_serializer:
            room["unread"] = unread_messages_count[counter]
            counter += 1
    else:
        chat_serializer = []

    # Serialize the private chats and add unread messages count to each chat
    contacts = []
    unread_messages_count = []
    for chat in privates:
        unread_messages = (
            Message.objects.filter(chat=chat).exclude(read_by__in=[user]).count()
        )
        unread_messages_count.append(unread_messages)
        contact = chat.members.all().exclude(username=username)
        contacts.append(contact[0])
    if len(contacts) > 0:
        serialized_profiles = FriendDataSerializer(
            contacts, many=True, context={"request": request}
        )
        serialized_profiles = serialized_profiles.data.copy()
        counter = 0
        for profile in serialized_profiles:
            profile["unread"] = unread_messages_count[counter]
            counter += 1

    else:
        serialized_profiles = []

    # ReOrganize the chats to single array
    recents = []
    if len(serialized_profiles) > 0:
        for chat in serialized_profiles:
            chat["chat_type"] = "PR"
            recents.append(chat)
    if len(chat_serializer) > 0:
        for chat in chat_serializer:
            del chat["members"]
            recents.append(chat)

    return recents


@api_view(["POST"])
def getFriendsAndChats(request):
    """
    Returns the user friends and 5 recent chats of the User
    """
    username = request.data["username"]
    user = User.objects.get(username=username)
    profile = Friendship.objects.get(user=user)
    friends_serializer = FriendDataSerializer(
        profile.friends, many=True, context={"request": request}
    )
    recents = get_recent_chats(request, username)
    return Response(
        {
            "friends": friends_serializer.data,
            "recent_chats": recents,
        }
    )
