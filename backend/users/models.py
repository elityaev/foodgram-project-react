from django.contrib.auth.models import AbstractUser
from django.db import models

ROLES = (
    ('user', 'Пользователь'),
    ('admin', 'Администратор')
)


class UserRole:
    USER = 'user'
    ADMIN = 'admin'


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    password = models.CharField(max_length=150)
    role = models.CharField(
        choices=ROLES,
        max_length=20,
        default=UserRole.USER
    )

    @property
    def is_user(self):
        return self.role == UserRole.USER

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
