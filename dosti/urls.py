from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    registerView,
    personalInfoView,
    userView,
    userSearchView,
    requestOperationView,
    requestRetriveView,
    friendsView,
    userSelfView,
    updatePersonalInfoView,
    mediaUpdateView,
    userBasicInfoView,
    passwordChangeView,
)


urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", registerView),
    path("register/personalInfo/", personalInfoView),
    path("account/changePassword/", passwordChangeView),
    path("personalInfo/update/", updatePersonalInfoView),
    path("personalInfo/update/media/", mediaUpdateView),
    path("users/search/", userSearchView),
    path("users/me/", userSelfView),
    path("users/user/", userView),
    path("users/user/basic/", userBasicInfoView),
    path("friends/requests/", requestRetriveView),
    path("friends/requests-operation/", requestOperationView),
    path("friends/", friendsView),
]
