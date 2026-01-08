# Push Notifications and Email Notifications Setup Guide

## Overview
This guide explains how to set up email and push notifications for the Swirl backend.

## Email Notifications

### 1. Configure Email Backend

Update `config/settings.py`:

```python
# For development (console backend - emails print to console)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# For production (SMTP)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"  # or your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "your-email@gmail.com"
EMAIL_HOST_PASSWORD = "your-app-password"
DEFAULT_FROM_EMAIL = "noreply@swirl.com"

# Frontend URL for email links
FRONTEND_URL = "https://your-frontend-domain.com"
```

### 2. Email Templates

Email templates are located in `templates/notifications/emails/`:
- `default.html` - Default template for all notifications
- `follow.html` - Template for follow notifications
- `comment.html` - Template for comment notifications
- Add more templates as needed for other action types

### 3. Usage

Email notifications are automatically sent when creating notifications:

```python
from apps.notifications.utils import create_notification

# Send both email and push
create_notification(
    user=target_user,
    actor=current_user,
    action_type='comment',
    target_object=post,
    send_email=True,  # Default: True
    send_push=True   # Default: True
)

# Only send push, no email
create_notification(
    user=target_user,
    actor=current_user,
    action_type='reaction',
    target_object=post,
    send_email=False,
    send_push=True
)
```

## Push Notifications (Firebase Cloud Messaging)

### 1. Install Firebase Admin SDK

```bash
pip install firebase-admin
```

### 2. Set Up Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select existing one
3. Go to Project Settings > Service Accounts
4. Click "Generate New Private Key" to download JSON credentials file
5. Save the file securely (e.g., `config/firebase-credentials.json`)

### 3. Configure Firebase in Settings

Add to `config/settings.py`:

```python
# Option 1: Path to credentials file
FIREBASE_CREDENTIALS_PATH = BASE_DIR / 'config' / 'firebase-credentials.json'

# Option 2: Or use environment variable (for production)
# FIREBASE_CREDENTIALS_JSON = os.environ.get('FIREBASE_CREDENTIALS_JSON')

# Frontend URL for notification links
FRONTEND_URL = "https://your-frontend-domain.com"
```

**Important:** Add `firebase-credentials.json` to `.gitignore` to keep credentials secure!

### 4. Frontend Setup (Register Device Tokens)

Your frontend needs to:
1. Request notification permission
2. Get FCM token
3. Register token with backend

**Example (JavaScript/React):**

```javascript
// Install Firebase SDK: npm install firebase

import { initializeApp } from 'firebase/app';
import { getMessaging, getToken } from 'firebase/messaging';

const firebaseConfig = {
  apiKey: "your-api-key",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "your-app-id"
};

const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);

// Request permission and get token
async function registerPushToken() {
  try {
    const permission = await Notification.requestPermission();
    if (permission === 'granted') {
      const token = await getToken(messaging, {
        vapidKey: 'your-vapid-key'
      });
      
      // Register token with backend
      await fetch('/api/notifications/push-token/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          token: token,
          device_type: 'web' // or 'ios', 'android'
        })
      });
    }
  } catch (error) {
    console.error('Error registering push token:', error);
  }
}
```

### 5. API Endpoints

**Register Push Token:**
```
POST /api/notifications/push-token/
Body: {
  "token": "fcm-device-token",
  "device_type": "web"  // or "ios", "android"
}
```

**Unregister Push Token:**
```
DELETE /api/notifications/push-token/{token}/
```

### 6. Usage

Push notifications are automatically sent when creating notifications:

```python
from apps.notifications.utils import create_notification

# Automatically sends push notification
create_notification(
    user=target_user,
    actor=current_user,
    action_type='comment',
    target_object=post,
    send_push=True  # Default: True
)
```

## Notification Preferences

You can extend the system to allow users to control notification preferences:

1. Add a `NotificationPreferences` model
2. Store user preferences (email_enabled, push_enabled, etc.)
3. Check preferences before sending notifications

## Testing

### Test Email Notifications

```python
# In Django shell
from apps.notifications.models import Notification
from apps.notifications.services import send_email_notification

notification = Notification.objects.first()
send_email_notification(notification)
```

### Test Push Notifications

```python
# In Django shell
from apps.notifications.models import Notification
from apps.notifications.services import send_push_notification

notification = Notification.objects.first()
send_push_notification(notification)
```

## Troubleshooting

### Email Issues
- Check SMTP settings
- Verify `DEFAULT_FROM_EMAIL` is set
- Check spam folder
- Review email backend logs

### Push Notification Issues
- Verify Firebase credentials are correct
- Check if device token is registered
- Ensure Firebase Admin SDK is initialized
- Check Firebase Console for delivery reports
- Review application logs for errors

## Security Notes

1. **Never commit Firebase credentials to version control**
2. **Use environment variables for production**
3. **Implement rate limiting** (already done)
4. **Validate device tokens** before storing
5. **Handle token expiration** gracefully
