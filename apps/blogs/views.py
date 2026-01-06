
from django.db.models import F
from rest_framework import generics, filters, permissions

from .permissions import IsCommentOwner, IsOwner

from .serializers import CommentSerializer, PostSerializer, CategorySerializer

from .models import Post, Category, Comment
# Create your views here

class PostsListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.active()
    serializer_class = PostSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    

    def get_queryset(self):
        qs = super().get_queryset().select_related("author")
        status = self.request.query_params.get('status')
        category = self.request.query_params.get('category')
        if status == 'draft':
            qs = qs.is_draft()
        elif status  == 'published':
            qs = qs.is_published()
        if category:
            qs = qs.filter(post__category=category)
        return qs

    def perform_create(self, serializer):
        print(serializer.validated_data)
        title : str = serializer.validated_data.get('title')
        content = serializer.validated_data.get('content') or None
        if content is None:
            content = title
        serializer.save(author=self.request.user, content=content)

class PostsUpdateView(generics.UpdateAPIView):
    queryset= Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsOwner]

    lookup_field = 'pk'
    lookup_url_kwarg='id'

    def perform_update(self, serializer):
        instance = serializer.save();
        if not instance.content:
            instance.content = instance.title
            instance.save()

class PostDeleteView(generics.DestroyAPIView):
    queryset= Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsOwner]
    lookup_field = 'pk'
    lookup_url_kwarg='id'

    def perform_destroy(self, serializer):
        instance = serializer.save();
        instance.is_deleted = True
        instance.save()

class PostRetrieveView(generics.RetrieveAPIView):
    queryset= Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsOwner]
    lookup_field = 'pk'
    lookup_url_kwarg='id'


class CommentsListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs["id"]
        return super().get_queryset().filter(post_id=post_id,parent__isnull=True).select_related('user')

    def perform_create(self, serializer):
        post_id = self.kwargs["id"]
        post = generics.get_object_or_404(Post, pk=post_id)
        serializer.save(post=post, user=self.request.user)

class RetrieveCommentView(generics.RetrieveAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'pk'
    lookup_url_kwarg = 'id'

class UpdateCommentView(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCommentOwner]
    lookup_field = 'pk'
    lookup_url_kwarg = 'id'

class DeleteCommentView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCommentOwner]
    lookup_field = 'pk'
    lookup_url_kwarg = 'id'

    def perform_destroy(self, instance):
        parent = instance.parent
        instance.delete()

        if parent:
            Comment.objects.filter(pk=parent.pk).update(
                reply_count=F("reply_count") - 1
            )

class RepliesListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(parent_id=self.kwargs['id']).select_related('user')

    def perform_create(self, serializer):
        user = self.request.user
        parent = generics.get_object_or_404(Comment, pk=self.kwargs['id'])
        serializer.save(
            user=user,
            parent=parent,
            post=parent.post
        )
        
        Comment.objects.filter(pk=parent.pk).update(
            reply_count=F("reply_count") + 1
        )


    
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'slug']
    permission_classes = [permissions.IsAuthenticated]