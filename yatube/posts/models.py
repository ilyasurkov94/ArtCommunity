from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'Выбери группу',
        max_length=200,
        help_text='Название группы'
    )
    slug = models.SlugField(unique=True)
    description = models.TextField(
        'Опиши группу',
        help_text='Описание группы'
    )

    class Meta:
        verbose_name = 'group'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Введи текст',
        help_text='Текст поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        help_text='Автор поста'
    )
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        help_text='Дата публикации'
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Поле группы',
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        help_text='Группа'
    )

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        'Введи текст',
        help_text='Добавь, пожалуйста, свой комментарий'
    )
    created = models.DateTimeField(
        'Дата создания комента',
        auto_now_add=True,
        help_text='Дата публикации комента'
    )

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        help_text='Кто подписан')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        help_text='На кого подписан')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'), name='unique_relations')
        ]

    def __str__(self):
        return self.text('User follows author')
