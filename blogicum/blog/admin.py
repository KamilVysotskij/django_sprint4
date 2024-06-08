from django.contrib import admin

from blog.models import Category, Location, Post


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
    )
    list_editable = (
        'description',
        'slug',
        'is_published',
    )
    search_fields = (
        'title',
        'description',
        'slug',
    )
    list_filter = ('title',)
    list_display_links = ('title',)
    ordering = ['slug']


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'is_published'
    )
    list_editable = (
        'name',
        'is_published',
    )
    search_fields = (
        'id',
        'name',
    )
    list_display_links = ('id',)
    ordering = ['id']


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'author',
        'category',
        'location',
        'is_published',
    )
    list_editable = (
        'author',
        'category',
        'location',
        'is_published'
    )
    search_fields = (
        'title',
        'text',
    )
    list_filter = (
        'author',
        'category',
        'is_published'
    )
    list_display_links = ('title',)
    ordering = ['author__first_name']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
