from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from groups.views import GroupViewSet, GroupMembershipViewSet, dashboard_view, chat_view, direct_message_view
from messaging.views import MessageViewSet
from users.views import login_view, logout_view, register_view


router = DefaultRouter()
router.register(r"groups", GroupViewSet, basename="group")
router.register(r"memberships", GroupMembershipViewSet, basename="membership")
router.register(r"messages", MessageViewSet, basename="message")


urlpatterns = [
    path("admin/", admin.site.urls),

    # API
    path("api/", include(router.urls)),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Web
    path("", login_view, name="login"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("chat/<int:group_id>/", chat_view, name="chat"),
    path("dm/<int:user_id>/", direct_message_view, name="direct_message"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
