from django.db import models
from django.conf import settings

from users.models import CustomUser


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

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Link(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Ссылка"
        verbose_name_plural = "Ссылки"


class CategoryGoodLink(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория полезная ссылка"
        verbose_name_plural = "Категории полезных ссылок"


class GoodLink(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField()
    category = models.ForeignKey(CategoryGoodLink, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Полезная ссылка"
        verbose_name_plural = "Полезные ссылки"


class Attachment(models.Model):
    file = models.FileField(upload_to='attachments/')  # Выберите папку, в которую будут загружаться файлы

    def __str__(self):
        return self.file.name

    class Meta:
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"


class Knowledge(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    links = models.ManyToManyField(Link, blank=True)
    attachments = models.ManyToManyField(Attachment, blank=True)  # Добавляем поле для прикрепленных файлов
    images = models.ManyToManyField(Image, blank=True)  # Добавляем поле для прикрепленных файлов

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "База знаний"
        verbose_name_plural = "База знаний"
