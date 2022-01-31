from django.db import models
from django.conf import settings
from django.db.models.signals import post_save


GENDERS = [("M", "male"), ("F", "female"), ("NS", "not specified")]
MARITAL_STATE = [("S", "single"), ("M", "maried"), ("E", "engaged")]


class UserProfile(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user"
    )
    profile_pic = models.ImageField(
        upload_to="profilesPics", max_length=255, null=True, blank=True
    )
    cover_photo = models.ImageField(
        upload_to="coverPhotos", max_length=255, null=True, blank=True
    )
    gender = models.CharField(choices=GENDERS, default="NS", max_length=2)
    date_of_birth = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=55, default="Add you Country")
    city = models.CharField(max_length=55, default="Add your City")
    workplace = models.CharField(max_length=55, blank=True, default="Add a workplace")
    bio = models.CharField(max_length=255, default="Add a bio")
    marital_state = models.CharField(choices=MARITAL_STATE, default="S", max_length=1)

    def get_full_name(self):
        return self.user.get_full_name()

    def get_image_url(self, request):
        return request.build_absolute_uri(self.profile_pic.url)


class Friendship(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owner"
    )
    friends = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="friends",
    )

    def __str__(self):
        return self.user.username

    def add_friend(self, account):
        """
        Add friend
        """
        if account not in self.friends.all():
            self.friends.add(account)

    def remove_friend(self, account):
        """
        Removes friend
        """
        if account in self.friends.all():
            self.friends.remove(account)

    def un_friend(self, target):
        """
        Removes friendship from both sides
        """
        user_friend_list = self

        # removing the friend from user friends list
        if target in self.friends.all():
            user_friend_list.remove_friend(target)

        target_profile = Friendship.objects.get(user=target)

        # removing user from target friend list
        if self.user in target_profile.friends.all():
            target_profile.remove_friend(self.user)

    def is_mutual_friend(self, account):

        if account in self.friends.all():
            return True
        return False


class FriendRequests(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sender"
    )
    reciver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reciver"
    )
    is_active = models.BooleanField(default=True, blank=True, null=True)
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sender.username

    def accept(self):

        """
        Accepts the request
        """

        senderFriendList = Friendship.objects.get(user=self.sender)
        if senderFriendList:
            senderFriendList.friends.add(user=self.reciver)
            reciverFriendlist = Friendship.objects.get(user=self.reciver)
            if reciverFriendlist:
                reciverFriendlist.add(self.sender)
                senderFriendList.save()
                reciverFriendlist.save()

        self.is_active = False
        self.save()

    def decline(self):
        self.is_active = False
        self.save()


def createFriendShip(instance, created, **kwargs):
    if created:
        Friendship.objects.create(user=instance)


def setDefaultProfilePic(instance, created, **kwargs):
    if created:
        if instance.gender == "F":
            instance.profile_pic = "https://raw.githubusercontent.com/BahirHakimy/file-storage-for-dostiapi/main/media/defaultFemale.png"
        else:
            instance.profile_pic = "https://raw.githubusercontent.com/BahirHakimy/file-storage-for-dostiapi/main/media/defaultMale.png"
        instance.cover_photo = "https://raw.githubusercontent.com/BahirHakimy/file-storage-for-dostiapi/main/media/defaultCover.jpg"
        instance.save()


post_save.connect(createFriendShip, sender=settings.AUTH_USER_MODEL)
post_save.connect(setDefaultProfilePic, sender=UserProfile)
