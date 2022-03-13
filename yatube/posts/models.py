from core.models import CreatedModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField(blank=True,
                            unique=True,
                            verbose_name='Имя Ссылки'
                            )
    description = models.TextField('Описание', blank=True)

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField('Текст поста')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts',
                               )
    group = models.ForeignKey(Group,
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL,
                              related_name='posts',
                              )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        # выводим текст поста
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             null=False,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             )
    author = models.ForeignKey(User,
                               related_name='comments',
                               on_delete=models.CASCADE,
                               )
    text = models.TextField('Текст комментария')
    created = models.DateTimeField('Дата публикации', auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(User,
                             null=False,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             )
    author = models.ForeignKey(User,
                               null=False,
                               related_name='following',
                               on_delete=models.CASCADE,
                               )
