from django.contrib.contenttypes.models import ContentType
from .models import Notification
from .services import send_email_notification, send_push_notification


def create_notification(user, actor, action_type, target_object=None, send_email=True, send_push=True):
    """
    Helper function to create a notification and optionally send email/push.
    
    Args:
        user: The user who will receive the notification
        actor: The user who performed the action
        action_type: Type of action (follow, comment, reply, reaction, bookmark)
        target_object: The object the action was performed on (Post, Comment, etc.)
        send_email: Whether to send email notification (default: True)
        send_push: Whether to send push notification (default: True)
    
    Returns:
        Notification object or None if notification couldn't be created
    """
    if user == actor and target_object is not None:
        return None
    
    try:
        if target_object is None:
            notification = Notification.objects.create(
                user=user,
                actor=actor,
                action_type=action_type,
                content_type=None,
                object_id=None
            )
        else:
            content_type = ContentType.objects.get_for_model(target_object)
            notification = Notification.objects.create(
                user=user,
                actor=actor,
                action_type=action_type,
                content_type=content_type,
                object_id=target_object.pk
            )
        
        # Send email notification if requested
        if send_email:
            email_sent = send_email_notification(notification)
            if email_sent:
                notification.email_sent = True
                notification.save(update_fields=['email_sent'])
        
        # Send push notification if requested
        if send_push:
            push_sent = send_push_notification(notification)
            if push_sent:
                notification.push_sent = True
                notification.save(update_fields=['push_sent'])
        
        return notification
    except Exception as e:
        print(f"Error creating notification: {e}")
        return None
