from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    
    def ready(self):
        """Initialize Firebase when app is ready."""
        try:
            from config.firebase_config import initialize_firebase
            initialize_firebase()
        except ImportError:
            # Firebase not installed or configured
            pass

