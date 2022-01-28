from django.contrib import admin
from .models import UserProfile, Friendship, FriendRequests

# # Register your models here.


class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "profile_pic",
        "gender",
    )


admin.site.register(UserProfile, UserProfileAdmin)


class FriendshipAdmin(admin.ModelAdmin):
    list_display = ("user",)


admin.site.register(Friendship, FriendshipAdmin)


class FriendRequestsAdmin(admin.ModelAdmin):
    list_display = ("sender", "reciver", "is_active", "time_stamp")


admin.site.register(FriendRequests, FriendRequestsAdmin)
