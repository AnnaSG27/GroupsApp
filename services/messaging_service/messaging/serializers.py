from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'id',
            'sender_id',
            'group_id',
            'content',
            'file',
            'status',
            'created_at'
        ]
