from rest_framework import serializers
from .models import Notification, PushNotificationToken
from apps.core.serializers import UserSummarySerializer


class NotificationSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    actor = UserSummarySerializer(read_only=True)
    target_object_id = serializers.IntegerField(source='object_id', read_only=True)
    target_content_type = serializers.CharField(source='content_type.model', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'actor',
            'action_type',
            'target_object_id',
            'target_content_type',
            'is_read',
            'email_sent',
            'push_sent',
            'created_at'
        ]
        read_only_fields = [
            'user',
            'actor',
            'action_type',
            'target_object_id',
            'target_content_type',
            'email_sent',
            'push_sent',
            'created_at'
        ]


class PushNotificationTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushNotificationToken
        fields = ['id', 'token', 'device_type', 'is_active', 'created_at']
        read_only_fields = ['id', 'is_active', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
