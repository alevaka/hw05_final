from django.contrib import admin

from .models import Comment, Follow, Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'text',
                    'pub_date',
                    'author',
                    'group'
                    )
    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_editable = ('group',)
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'user',
                    'author',
                    )
    list_filter = ('user', 'author',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('post',
                    'author',
                    'text',
                    'created',
                    )
    search_fields = ('text',)
    list_filter = ('author', 'created',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)

admin.site.register(Group)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
