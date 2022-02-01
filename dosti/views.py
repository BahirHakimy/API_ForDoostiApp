import json
import os
import base64
import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    parser_classes,
    permission_classes,
)
from rest_framework.parsers import FormParser, MultiPartParser
from .serializers import (
    FriendRequestSerializer,
    User,
    UserCreateSerializer,
    UserCreateProfileSerializer,
    UserSelfProfileSerializer,
    UserSearchProfileSerializer,
    UserProfileSerializer,
    FriendsSerializer,
    UserSelfSerializer,
)
from .models import Friendship, UserProfile, FriendRequests
from rest_framework.permissions import AllowAny
from django.core.files.base import ContentFile
import datetime


@api_view(["POST"])
@permission_classes([AllowAny])
def registerView(request):
    user = UserCreateSerializer(data=request.data)
    gender = request.data["gender"]
    if user.is_valid():
        result = user.save()
        UserProfile.objects.create(user=result, gender=gender)
        return Response(
            {"message": "Registeration successfull"},
            status=status.HTTP_201_CREATED,
        )
    else:
        return Response({"errors": user.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def passwordChangeView(request):
    username = request.data["username"]
    current_password = request.data["currentPassword"]
    new_password = request.data["newPassword"]
    user = User.objects.get(username=username)
    if user:
        if user.check_password(current_password):
            if current_password == new_password:
                return Response(
                    {"message": "New password cant be your old password"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.set_password(new_password)
            user.save()
            return Response(
                {"message": "Password changed successfully"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Current password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    else:
        return Response(
            {"message": "no users with the given username"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def personalInfoView(request):
    username = request.data["username"]
    try:
        profile_pic = request.data["profile_pic"]
    except KeyError:
        profile_pic = None

    user = User.objects.get(username=username)
    profile = UserProfile.objects.get(user=user)

    if profile_pic:
        image = ContentFile(base64.urlsafe_b64decode(profile_pic), f"{user.id}.jpg")
        profile.profile_pic = image

    serializer = UserCreateProfileSerializer(profile, data=request.data, many=False)
    if serializer.is_valid():
        serializer.save()
    else:
        print(serializer.errors)
        return Response(
            serializer.error_messages, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    profile.save()
    return Response(
        {"message": "Information saved successfully"}, status=status.HTTP_200_OK
    )


def delete_file_from_github(file):
    username = os.environ.get("GITHUB_USERNAME")
    token = os.environ.get("GITHUB_ACCESS_TOKEN")
    url = f"https://api.github.com/repos/BahirHakimy/file-storage-for-dostiapi/contents/media/{file}"
    response = requests.get(url, auth=(username, token))
    message = f"deleted file: {file}"
    sha = json.loads(response.text)["sha"]
    payload = {"sha": sha, "message": message}
    req = requests.delete(url, auth=(username, token), params=payload)
    print(f"Delete request status code: HTTP-{req.status_code}")


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def mediaUpdateView(request):
    username = request.data["username"]
    imageType = request.data["type"]
    image = request.data["image"]

    user = User.objects.get(username=username)
    profile = UserProfile.objects.get(user=user)

    if user and profile:
        if imageType == "profile":
            photo = ContentFile(
                base64.urlsafe_b64decode(image),
                f"{user.id}_{datetime.datetime.now()}profile.jpg",
            )
            if profile.profile_pic:
                if not profile.profile_pic.name.split("media/")[1].startswith(
                    "default"
                ):
                    delete_file_from_github(profile.profile_pic.name.split("media/")[1])
            profile.profile_pic = photo
        elif imageType == "cover":
            photo = ContentFile(
                base64.urlsafe_b64decode(image),
                f"{user.id}_{datetime.datetime.now()}cover.jpg",
            )
            if profile.cover_photo:
                if not profile.cover_photo.name.split("media/")[1].startswith(
                    "default"
                ):
                    delete_file_from_github(profile.cover_photo.name.split("media/")[1])
            profile.cover_photo = photo
        else:
            return Response(
                {"message": "Image type is not valid"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        profile.save()
        return Response({"message": "Update Successfull"}, status=status.HTTP_200_OK)

    else:
        return Response(
            {"message": "User is not not fount"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
def updatePersonalInfoView(request):
    username = request.data["username"]
    user = User.objects.get(username=username)
    profile = UserProfile.objects.get(user=user)
    userSerializer = UserSelfSerializer(user, request.data, many=False)
    profileSerializer = UserCreateProfileSerializer(profile, request.data, many=False)
    if userSerializer.is_valid() and profileSerializer.is_valid():
        userSerializer.save()
        profileSerializer.save()
        return Response({"message": "Information successfully updated."})
    else:
        print(userSerializer.errors)
        print(profileSerializer.errors)
        return Response(
            {"message": "Something went wrong"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def userSearchView(request):
    serachString = request.data["search"]
    currentUser = request.data["currentUser"]
    users = User.objects.filter(username__contains=serachString)
    profiles = []
    if users:
        for user in users:
            if user.username == currentUser:
                continue
            profile = UserProfile.objects.get(user=user)
            serializer = UserSearchProfileSerializer(
                profile, context={"request": request}
            )

            profiles.append(serializer.data)

        return Response(profiles, status=status.HTTP_200_OK)
    else:
        return Response({"message": "No users found!"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def userBasicInfoView(request):
    username = request.data["username"]
    user = User.objects.get(username=username)

    if user:

        profile = UserProfile.objects.get(user=user)
        serializer = UserSearchProfileSerializer(profile, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(
            {"message": "User Not Found!"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
def requestOperationView(request):
    username = request.data["username"]
    target = request.data["friend"]
    operation = request.data["operation"]
    user = User.objects.get(username=username)
    account = User.objects.get(username=target)
    if operation == "add":
        friendRequest = FriendRequests.objects.create(
            sender=user, reciver=account, is_active=True
        )
        friendRequest.save()
        return Response(
            {"message": "Friend Request Sent!"}, status=status.HTTP_202_ACCEPTED
        )
    elif operation == "accept":
        try:
            friendRequest = FriendRequests.objects.get(
                sender=account, reciver=user, is_active=True
            )
            userFriends = Friendship.objects.get(user=user)
            userFriends.friends.add(account)
            targetFriends = Friendship.objects.get(user=account)
            targetFriends.friends.add(user)
            friendRequest.is_active = False
            userFriends.save()
            targetFriends.save()
            friendRequest.save()
            return Response(
                {"message": "Friend Request Accepted!"}, status=status.HTTP_202_ACCEPTED
            )
        except:
            return Response(
                {"message": "Friend Request Not Found"},
                status=status.HTTP_404_NOT_FOUND,
            )
    elif operation == "delete":
        try:
            friendRequest = FriendRequests.objects.get(
                reciver=user, sender=account, is_active=True
            )
            friendRequest.is_active = False
            friendRequest.save()
            return Response(
                {"message": "Friend Request Declined!"}, status=status.HTTP_202_ACCEPTED
            )
        except:
            return Response(
                {"message": "Friend Request Not Found"},
                status=status.HTTP_404_NOT_FOUND,
            )
    elif operation == "cancel":
        try:
            friendRequest = FriendRequests.objects.get(
                reciver=account, sender=user, is_active=True
            )
            friendRequest.is_active = False
            friendRequest.save()
            return Response(
                {"message": "Unsent Friend Request!"}, status=status.HTTP_202_ACCEPTED
            )
        except:
            return Response(
                {"message": "Friend Request Not Found"},
                status=status.HTTP_404_NOT_FOUND,
            )
    elif operation == "unFriend":
        try:
            friendshipProfile = Friendship.objects.get(user=user)
            friendshipProfile.un_friend(account)
            return Response(
                {"message": "Friend Removed Successfully!"},
                status=status.HTTP_202_ACCEPTED,
            )
        except:
            return Response(
                {"message": "Friend Request Not Found"},
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["POST"])
def requestRetriveView(request):

    username = request.data["username"]
    user = User.objects.get(username=username)
    requests = FriendRequests.objects.filter(reciver=user, is_active=True)
    if requests.exists():
        serializer = FriendRequestSerializer(
            requests, context={"request": request}, many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"message": "No New Requests"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def friendsView(request):
    user = User.objects.get(username=request.data["username"])
    friends = Friendship.objects.get(user=user)
    serializer = FriendsSerializer(friends, context={"request": request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def userSelfView(request):

    user = User.objects.get(username=request.data["username"])

    if user:
        profile = UserProfile.objects.get(user=user)
        serializer = UserSelfProfileSerializer(profile, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(
            {"message": "no user found with given username!"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
def userView(request):

    user = User.objects.get(username=request.data["username"])
    current_user = request.data["currentUser"]
    if user:
        profile = UserProfile.objects.get(user=user)
        serializer = UserProfileSerializer(
            profile, context={"current_user": current_user, "request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response()
