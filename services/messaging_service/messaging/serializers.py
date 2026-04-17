from rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    sender_id = serializers.IntegerField()
    sender_name = serializers.CharField()
    group_id = serializers.IntegerField()
    content = serializers.CharField()
    file = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    status = serializers.CharField(required=False)
    created_at = serializers.DateTimeField(read_only=True)
