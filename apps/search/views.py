from rest_framework import generics, filters, permissions
from django.db.models import Q

from apps.blogs.models import Post
from apps.blogs.serializers import PostSerializer


class PostSearchView(generics.ListAPIView):
    """
    Search endpoint for posts with advanced filtering options.
    
    Query parameters:
    - q: Search query (searches in title, content, author name, category name, tags)
    - status: Filter by status (draft/published)
    - category: Filter by category ID or slug
    - author: Filter by author ID
    - tags: Filter by tag names (comma-separated)
    - ordering: Order results (e.g., '-created_at', 'title', '-reaction_count')
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'author__email', 'author__first_name', 'author__last_name', 
                     'category__name', 'tags__name']
    ordering_fields = ['created_at', 'updated_at', 'title', 'reaction_count', 'comment_count', 'bookmark_count']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Post.objects.active().select_related('author', 'category').prefetch_related('tags')
        
        # Get query parameters
        search_query = self.request.query_params.get('q', None)
        status = self.request.query_params.get('status', None)
        category = self.request.query_params.get('category', None)
        author_id = self.request.query_params.get('author', None)
        tags = self.request.query_params.get('tags', None)
        
        # Apply search query if provided
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(author__first_name__icontains=search_query) |
                Q(author__last_name__icontains=search_query) |
                Q(author__email__icontains=search_query) |
                Q(category__name__icontains=search_query) |
                Q(tags__name__icontains=search_query)
            ).distinct()
        
        # Filter by status
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by category (can be ID or slug)
        if category:
            try:
                # Try as ID first
                category_id = int(category)
                queryset = queryset.filter(category_id=category_id)
            except ValueError:
                # If not an integer, treat as slug
                queryset = queryset.filter(category__slug=category)
        
        # Filter by author
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
        # Filter by tags
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            queryset = queryset.filter(tags__name__in=tag_list).distinct()
        
        return queryset

