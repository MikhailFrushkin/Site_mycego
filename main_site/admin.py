from django.contrib import admin
from .models import Announcement, Image


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
