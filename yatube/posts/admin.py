from django.contrib import admin
from .models import Post, Group, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group',)
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'description',)
    list_editable = ('title',)
    search_fields = ('description',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'text', 'created',)
    list_editably = ('pk', 'text',)
    search_fields = ('author', 'text',)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
