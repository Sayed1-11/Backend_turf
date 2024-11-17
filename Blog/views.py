from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import BlogPost, Tag, Like
from .serializers import BlogPostSerializer, TagSerializer, LikeSerializer
from rest_framework import viewsets,filters
from django_filters.rest_framework import DjangoFilterBackend

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tags']
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        """
        Adds the request to the serializer context.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """
        Endpoint to like or dislike a blog post.
        """
        blog_post = self.get_object()
        if is_like is None:
            return Response({"error": "is_like field is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        like, created = Like.objects.update_or_create(
            user=request.user,
            blog_post=blog_post,
        )
        action = "liked" if is_like else "disliked"
        message = f"You have {action} the blog post."
        return Response({"message": message}, status=status.HTTP_200_OK)


class LikeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing likes.
    """
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
