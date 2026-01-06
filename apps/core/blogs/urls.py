from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.PostsListCreateView.as_view(), name='list-create-post'),
    path('posts/<int:id>/', views.PostRetrieveView.as_view(), name='retrieve-post'),
    path('posts/<int:id>/update/', views.PostsUpdateView.as_view(), name='update-post'),
    path('posts/<int:id>/delete/', views.PostDeleteView.as_view(), name='delete-post'),
    path('posts/<int:id>/comments/', views.CommentsListCreateView.as_view(), name='list-create-post-comments'),
    path('comments/<int:id>/', views.RetrieveCommentView.as_view(), name='retrieve-comment'),
    path('comments/<int:id>/delete/', views.DeleteCommentView.as_view(), name='delete-comment'),
    path('comments/<int:id>/update/', views.UpdateCommentView.as_view(), name='update-comment'),
    path('comments/<int:id>/replies/', views.RepliesListCreateView.as_view(), name='reply-comment'),
    path('categories/', views.CategoryListCreateView.as_view(), name='list-create-category'),
]
