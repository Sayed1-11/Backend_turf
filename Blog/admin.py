from django.contrib import admin
from .models import Like,BlogPost,Tag
# Register your models here.
admin.site.register(BlogPost)
admin.site.register(Tag)
admin.site.register(Like)