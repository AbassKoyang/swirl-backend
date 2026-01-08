from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='list-notifications'),
    path('<int:id>/read/', views.MarkNotificationReadView.as_view(), name='mark-notification-read'),
    path('push-token/', views.RegisterPushTokenView.as_view(), name='register-push-token'),
    path('push-token/<str:token>/', views.UnregisterPushTokenView.as_view(), name='unregister-push-token'),
]

