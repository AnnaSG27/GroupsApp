from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from .models import Message
from .serializers import MessageSerializer
from groups.models import GroupMembership


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(
            group__memberships__user=self.request.user
        ).distinct()

    def perform_create(self, serializer):
        group = serializer.validated_data["group"]

        is_member = GroupMembership.objects.filter(
            user=self.request.user,
            group=group
        ).exists()

        if not is_member:
            raise PermissionDenied("No perteneces a este grupo.")

        msg = serializer.save(sender=self.request.user)
        # broadcast to channel layer for realtime updates
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"group_{msg.group.id}",
            {
                'type': 'chat.message',
                'message': {
                    'sender': msg.sender.username,
                    'content': msg.content,
                    'file_url': msg.file.url if msg.file else '',
                    'created_at': msg.created_at.isoformat(),
                }
            }
        )
