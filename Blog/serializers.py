from rest_framework import serializers
from .models import BlogPost, Tag,Like

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'blog_post', 'created_at','is_like']
        read_only_fields = ['id', 'created_at']

class BlogPostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)  # Nested representation
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True, source='tags'
    )
    total_likes = serializers.ReadOnlyField()
    is_liked_by_user = serializers.SerializerMethodField()
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'content', 'image', 'author', 'created_at',
            'updated_at', 'tags', 'tag_ids', 'total_likes','is_liked_by_user',
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        blog_post = BlogPost.objects.create(**validated_data)
        blog_post.tags.set(tags)
        return blog_post

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags:
            instance.tags.set(tags)  # Update the tags
        return instance
    
    def get_is_liked_by_user(self, obj):
        """
        Determines if the currently authenticated user has liked this blog post.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(blog_post=obj, user=request.user, is_like=True).exists()
        return False