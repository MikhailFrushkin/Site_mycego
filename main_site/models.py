from django.db import models
from django.conf import settings


class Announcement(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Текст объявления')
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_pinned = models.BooleanField(default=False, verbose_name='Закреплено')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Автор')
    images = models.ManyToManyField('Image', blank=True, verbose_name='Фотографии')
    url = models.URLField(blank=True, null=True, verbose_name='Ссылка')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-date_created']


class Image(models.Model):
    image = models.ImageField(upload_to='announcements/', verbose_name='Фотография')

    def __str__(self):
        return str(self.image)
