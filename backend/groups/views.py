from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.shortcuts import redirect, render, get_object_or_404
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.contrib import messages

from .models import Group, GroupMembership
from .serializers import GroupSerializer, GroupMembershipSerializer
from messaging.models import Message

User = get_user_model()

class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Group.objects.filter(
            memberships__user=self.request.user
        ).distinct()

    def perform_create(self, serializer):
        group = serializer.save(created_by=self.request.user)
        GroupMembership.objects.create(
            user=self.request.user,
            group=group,
            role="admin"
        )


class GroupMembershipViewSet(viewsets.ModelViewSet):
    queryset = GroupMembership.objects.all()
    serializer_class = GroupMembershipSerializer
    permission_classes = [IsAuthenticated]

@login_required
def dashboard_view(request):
    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        description = (request.POST.get("description") or "").strip()

        if name:
            group = Group.objects.create(
                name=name,
                description=description,
                created_by=request.user
            )
            GroupMembership.objects.create(
                user=request.user,
                group=group,
                role="admin"
            )
            return redirect("chat", group_id=group.id)

        return redirect("dashboard")

    memberships = request.user.memberships.select_related("group")
    group_memberships = memberships.filter(group__is_direct=False)
    direct_memberships = memberships.filter(group__is_direct=True)

    return render(request, "dashboard.html", {
        "memberships": group_memberships,
        "direct_memberships": direct_memberships,
    })


@login_required
@ensure_csrf_cookie
@csrf_protect
def chat_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    # mark current user online when opening chat
    if request.method == "GET" and hasattr(request.user, 'is_online'):
        request.user.is_online = True
        request.user.save(update_fields=["is_online"])

    is_member = GroupMembership.objects.filter(user=request.user, group=group).exists()
    if not is_member:
        messages.error(request, "No perteneces a este grupo.")
        return redirect("dashboard")

    chat_messages = group.messages.select_related("sender").order_by("created_at")
    members = group.memberships.select_related("user")
    # also collect the user's groups for the sidebar
    user_groups = request.user.memberships.select_related("group")

    if request.method == "POST":
        # handle send message
        if "send_message" in request.POST:
            content = request.POST.get("content", "").strip()
            file = request.FILES.get("file")

            if content or file:
                msg = Message.objects.create(
                    sender=request.user,
                    group=group,
                    content=content,
                    file=file
                )
                # broadcast via channels
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"group_{group.id}",
                    {
                        'type': 'chat.message',
                        'message': {
                            'sender': request.user.username,
                            'content': msg.content,
                            'file_url': msg.file.url if msg.file else '',
                            'created_at': msg.created_at.isoformat(),
                        }
                    }
                )
            return redirect("chat", group_id=group.id)

        # handle invite user
        if "invite_user" in request.POST:
            username = request.POST.get("username", "").strip()

            if username:
                try:
                    user_to_add = User.objects.get(username=username)

                    membership, created = GroupMembership.objects.get_or_create(
                        user=user_to_add,
                        group=group,
                        defaults={"role": "member"}
                    )

                    if created:
                        messages.success(request, f"{username} fue agregado al grupo.")
                    else:
                        messages.info(request, f"{username} ya está en el grupo.")

                except User.DoesNotExist:
                    messages.error(request, "Usuario no encontrado.")
            else:
                messages.error(request, "Ingresa un nombre de usuario.")

            return redirect("chat", group_id=group.id)

    return render(request, "chat.html", {
        "group": group,
        "group_name": group.display_name(),
        "chat_messages": chat_messages,
        "members": members,
        "user_groups": user_groups,
    })

# helper endpoint for direct messaging
@login_required
@csrf_protect
def direct_message_view(request, user_id):
    try:
        other = get_object_or_404(User, id=user_id)
        if other == request.user:
            messages.error(request, "No puedes enviarte mensajes a ti mismo.")
            return redirect("dashboard")
        
        group, created = Group.get_or_create_direct(request.user, other)
        if created:
            messages.success(request, f"Conversación iniciada con {other.username}")
        return redirect("chat", group_id=group.id)
    except Exception as e:
        messages.error(request, f"Error al iniciar conversación: {str(e)}")
        return redirect("dashboard")
