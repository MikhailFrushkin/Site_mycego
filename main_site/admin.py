from django.contrib import admin
from .models import Announcement, Image, Category, Knowledge, Link, Attachment, GoodLink, CategoryGoodLink


class ImageInline(admin.TabularInline):
    model = Announcement.images.through
    extra = 1  # Указывает, сколько пустых форм для выбора фотографий отображать


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date_created', 'is_pinned')
    list_filter = ('date_created', 'is_pinned')
    search_fields = ('title', 'content', 'author__username')
    date_hierarchy = 'date_created'

    # Подключаем пользовательский класс для выбора фотографий
    inlines = [ImageInline]


admin.site.register(Image)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(Knowledge)
class KnowledgeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'created_at', 'updated_at')
    list_filter = ('category', 'author')
    search_fields = ('title', 'content')
    filter_horizontal = ('links', 'attachments')


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'url')


@admin.register(GoodLink)
class GoodLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'url')


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('file',)


@admin.register(CategoryGoodLink)
class CategoryGoodLinkAdmin(admin.ModelAdmin):
    list_display = ('name',)
