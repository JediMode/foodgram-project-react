from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(
        'Электронная почта', max_length=254, unique=True
    )
    username = models.CharField(
        'Логин', max_length=150, unique=True
    )
    password = models.CharField(
        'Пароль', max_length=150
    )
    first_name = models.CharField(
        'Имя', max_length=150
    )
    last_name = models.CharField(
        'Фамилия', max_length=150
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name='follower', verbose_name='Подписчик')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                               related_name='following', verbose_name='Автор')

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='self_following'
            ),
        ]

    def __str__(self):
        return f'{self.user} following {self.author}'
