from django.urls import path
from .views import (
    load_messages,
    roomsListView,
    roomsSearchView,
    createRoomView,
    getChat,
    getFriendsAndChats,
    file_upload_endpoint,
)

urlpatterns = [
    path("rooms/list/", roomsListView),
    path("rooms/search/", roomsSearchView),
    path("rooms/create/", createRoomView),
    path("rooms/get/", getChat),
    path("rooms/messages/", load_messages),
    path("rooms/messages/upload/", file_upload_endpoint),
    path("rooms/friends-and-recent/", getFriendsAndChats),
]
