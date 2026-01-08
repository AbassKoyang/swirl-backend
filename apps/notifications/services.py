from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def send_email_notification(notification):
    """
    Send email notification to user.
    
    Args:
        notification: Notification instance
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        user = notification.user
        actor = notification.actor
        action_type = notification.get_action_type_display()
        
        # Generate email subject and message based on action type
        subject = get_notification_subject(notification)
        message = get_notification_message(notification)
        
        # Send email
        send_mail(
            subject=subject,
            message=strip_tags(message),  # Plain text version
            html_message=message,  # HTML version
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Email notification sent to {user.email} for {action_type}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email notification: {e}")
        return False


def get_notification_subject(notification):
    """Generate email subject based on notification type."""
    actor_name = notification.actor.get_full_name() or notification.actor.email
    
    subjects = {
        'follow': f"{actor_name} started following you",
        'comment': f"{actor_name} commented on your post",
        'reply': f"{actor_name} replied to your comment",
        'reaction': f"{actor_name} reacted to your post",
        'bookmark': f"{actor_name} bookmarked your post",
        'sign_up': "Welcome to Swirl!",
        'log_in': "Welcome back to Swirl!",
    }
    
    return subjects.get(notification.action_type, "You have a new notification")


def get_notification_message(notification):
    """Generate HTML email message based on notification type."""
    actor_name = notification.actor.get_full_name() or notification.actor.email
    actor_email = notification.actor.email
    
    # Get target object URL if available
    target_url = get_notification_url(notification)
    
    context = {
        'actor_name': actor_name,
        'actor_email': actor_email,
        'action_type': notification.get_action_type_display(),
        'target_url': target_url,
        'notification': notification,
    }
    
    # Render email template
    try:
        message = render_to_string(
            f'notifications/emails/{notification.action_type}.html',
            context
        )
    except:
        # Fallback to default template if specific template doesn't exist
        message = render_to_string('notifications/emails/default.html', context)
    
    return message


def get_notification_url(notification):
    """Generate URL to the target object."""
    if notification.target_object:
        if hasattr(notification.target_object, 'get_absolute_url'):
            return notification.target_object.get_absolute_url()
        # Fallback URLs based on content type
        if notification.content_type.model == 'post':
            return f"{settings.FRONTEND_URL}/posts/{notification.object_id}"
        elif notification.content_type.model == 'comment':
            return f"{settings.FRONTEND_URL}/comments/{notification.object_id}"
    
    return f"{settings.FRONTEND_URL}/notifications"


def send_push_notification(notification):
    """
    Send push notification using Firebase Cloud Messaging (FCM).
    
    Args:
        notification: Notification instance
    
    Returns:
        bool: True if push notification sent successfully, False otherwise
    """
    try:
        from apps.notifications.models import PushNotificationToken
        try:
            from firebase_admin import messaging
        except ImportError:
            logger.error("Firebase Admin SDK not installed. Install with: pip install firebase-admin")
            return False
        
        # Get user's FCM tokens
        tokens = PushNotificationToken.objects.filter(
            user=notification.user,
            is_active=True
        ).values_list('token', flat=True)
        
        if not tokens:
            logger.info(f"No FCM tokens found for user {notification.user.email}")
            return False
        
        # Prepare notification message
        title = get_notification_subject(notification)
        body = get_notification_body(notification)
        
        # Create FCM message
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data={
                'notification_id': str(notification.id),
                'action_type': notification.action_type,
                'type': 'notification',
            },
            tokens=list(tokens),
        )
        
        # Send message
        response = messaging.send_multicast(message)
        
        if response.failure_count > 0:
            logger.warning(f"Failed to send {response.failure_count} push notifications")
            # Handle failed tokens (mark as inactive)
            for idx, resp in enumerate(response.responses):
                if not resp.success:
                    if resp.exception.code == 'registration-token-not-registered':
                        # Token is invalid, mark as inactive
                        token_obj = PushNotificationToken.objects.filter(
                            token=tokens[idx]
                        ).first()
                        if token_obj:
                            token_obj.is_active = False
                            token_obj.save()
        
        logger.info(f"Push notification sent to {response.success_count} devices")
        return response.success_count > 0
        
    except ImportError:
        logger.error("Firebase Admin SDK not installed. Install with: pip install firebase-admin")
        return False
    except Exception as e:
        logger.error(f"Error sending push notification: {e}")
        return False


def get_notification_body(notification):
    """Generate push notification body text."""
    actor_name = notification.actor.get_full_name() or notification.actor.email
    
    bodies = {
        'follow': f"{actor_name} started following you",
        'comment': f"{actor_name} commented on your post",
        'reply': f"{actor_name} replied to your comment",
        'reaction': f"{actor_name} reacted to your post",
        'bookmark': f"{actor_name} bookmarked your post",
        'sign_up': "Welcome to Swirl! Get started by exploring posts.",
        'log_in': "Welcome back! Check out what's new.",
    }
    
    return bodies.get(notification.action_type, "You have a new notification")
