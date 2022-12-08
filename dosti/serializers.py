from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import UserProfile, Friendship, FriendRequests

User = get_user_model()
GENDERS = [("M", "male"), ("F", "female"), ("NS", "not specified")]


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data["username"],
            validated_data["email"],
            validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        return user


class UserCreateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "date_of_birth",
            "country",
            "city",
            "workplace",
            "bio",
            "marital_state",
        )


class UserSelfSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")


class UserSelfProfileSerializer(serializers.ModelSerializer):

    user = UserSelfSerializer(read_only=True)
    fullname = serializers.ReadOnlyField(source="get_full_name")
    profile_pic = serializers.ImageField(use_url=True)
    cover_photo = serializers.ImageField(use_url=True)

    class Meta:
        model = UserProfile
        fields = (
            "user",
            "fullname",
            "country",
            "city",
            "workplace",
            "date_of_birth",
            "profile_pic",
            "cover_photo",
            "gender",
            "bio",
            "marital_state",
        )


class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username",)


class UserSearchProfileSerializer(serializers.ModelSerializer):
    user = UserSearchSerializer(read_only=True)
    fullname = serializers.ReadOnlyField(source="get_full_name")
    profile_pic = serializers.ImageField(use_url=True)

    class Meta:
        model = UserProfile
        fields = ("user", "fullname", "profile_pic")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username",)


class UserProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    fullname = serializers.ReadOnlyField(source="get_full_name")
    friendship_state = serializers.SerializerMethodField("get_friendship_state")
    profile_pic = serializers.ImageField(use_url=True)
    cover_photo = serializers.ImageField(use_url=True)

    class Meta:
        model = UserProfile
        fields = (
            "user",
            "fullname",
            "country",
            "city",
            "workplace",
            "profile_pic",
            "cover_photo",
            "date_of_birth",
            "friendship_state",
        )

    def get_friendship_state(self, object):

        user = User.objects.get(username=self.context.get("current_user"))
        target = object.user
        is_friends = Friendship.objects.get(user=user).is_mutual_friend(target)

        try:
            request_sent = FriendRequests.objects.get(
                sender=user, reciver=target, is_active=True
            )
        except:
            request_sent = None
        try:
            request_recived = FriendRequests.objects.get(
                sender=target, reciver=user, is_active=True
            )
        except:
            request_recived = None

        if is_friends:
            return "success"
        if not is_friends and request_sent:
            return "pending"
        if not is_friends and request_recived:
            return "waiting"
        else:
            return "idle"


class FriendDataSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField("get_profile_pic")
    fullname = serializers.ReadOnlyField(source="get_full_name")

    class Meta:
        model = User
        fields = ("username", "fullname", "profile_pic")

    def get_profile_pic(self, object):
        user = UserProfile.objects.get(user=object)
        # if type(self.context) == set:
        #     a = []
        #     for e in self.context:
        #         if type(e) != str:
        #             a.append(e)

        #     request = a[0]
        #     return user.get_image_url(request)
        # else:
        return user.get_image_url(self.context["request"])


class FriendRequestSerializer(serializers.ModelSerializer):

    sender = FriendDataSerializer(read_only=True)

    class Meta:
        model = FriendRequests
        fields = ("sender",)


class FriendsSerializer(serializers.ModelSerializer):

    friends = FriendDataSerializer(read_only=True, many=True)

    class Meta:
        model = Friendship
        fields = ("friends",)


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("image",)
