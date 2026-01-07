from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.PostSearchView.as_view(), name='search-posts'),
]

