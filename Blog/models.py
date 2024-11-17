from django.db import models
from User.models import UserModel

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/')
    author = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='blog_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, related_name='blog_posts')

    def __str__(self):
        return self.title
    class Meta:
        db_table = 'custom_blogpost_name'
    
    @property
    def total_likes(self):
        return self.likes.filter(is_like=True).count()

class Like(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='likes')
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='likes')
    is_like = models.BooleanField()  # True for like, False for dislike
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'blog_post')