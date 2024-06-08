from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.urls import reverse

from core.models import BaseModel


User = get_user_model()


class Category(BaseModel):
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=256)
    description = models.TextField(
        verbose_name='Описание')
    slug = models.SlugField(
        verbose_name='Идентификатор',
        help_text=('Идентификатор страницы для URL; разрешены символы '
                   'латиницы, цифры, дефис и подчёркивание.'),
        unique=True)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField(
        verbose_name='Название места',
        max_length=256)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class PublishedPostManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )


class Post(BaseModel):
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=256)
    image = models.ImageField('Фото', upload_to='posts_images', blank=True)
    text = models.TextField(
        verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=('Если установить дату и время в будущем '
                   '— можно делать отложенные публикации.'))
    author = models.ForeignKey(
        User,
        related_name='posts',
        verbose_name='Автор публикации',
        on_delete=models.CASCADE)
    location = models.ForeignKey(
        Location,
        related_name='posts',
        verbose_name='Местоположение',
        on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(
        Category,
        related_name='posts',
        verbose_name='Категория',
        on_delete=models.SET_NULL, null=True)
    objects = models.Manager()
    published_objects = PublishedPostManager()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title



class Comment(models.Model):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)
