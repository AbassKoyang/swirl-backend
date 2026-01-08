from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Notification, PushNotificationToken
from .serializers import NotificationSerializer, PushNotificationTokenSerializer
from .throttles import NotificationReadRateThrottle, NotificationMarkReadRateThrottle


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [NotificationReadRateThrottle]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).select_related('user', 'actor').order_by('-created_at')


class MarkNotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [NotificationMarkReadRateThrottle]

    def post(self, request, id, **kwargs):
        notification = get_object_or_404(
            Notification,
            pk=id,
            user=request.user
        )
        
        if notification.is_read:
            return Response(
                {"message": "Notification is already marked as read"},
                status=status.HTTP_200_OK
            )
        
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        
        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterPushTokenView(generics.CreateAPIView):
    """
    Register a device token for push notifications.
    POST /api/notifications/push-token/
    """
    serializer_class = PushNotificationTokenSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        token = serializer.validated_data['token']
        device_type = serializer.validated_data.get('device_type', 'web')
        
        # Update or create token
        token_obj, created = PushNotificationToken.objects.update_or_create(
            token=token,
            defaults={
                'user': self.request.user,
                'device_type': device_type,
                'is_active': True,
            }
        )
        
        return token_obj


class UnregisterPushTokenView(APIView):
    """
    Unregister a device token for push notifications.
    DELETE /api/notifications/push-token/{token}/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, token, **kwargs):
        try:
            token_obj = PushNotificationToken.objects.get(
                token=token,
                user=request.user
            )
            token_obj.is_active = False
            token_obj.save()
            return Response(
                {"message": "Push token unregistered successfully"},
                status=status.HTTP_200_OK
            )
        except PushNotificationToken.DoesNotExist:
            return Response(
                {"error": "Token not found"},
                status=status.HTTP_404_NOT_FOUND
            )
