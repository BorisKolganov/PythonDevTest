from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, BaseUserManager
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'пользователи'

    email = models.EmailField(verbose_name='Email', unique=True)
    name = models.CharField(verbose_name='Имя', null=True, max_length=200)
    company = models.CharField(verbose_name='Компания', null=True, max_length=200)
    phone = PhoneNumberField(verbose_name='Телефон', null=True, max_length=200)
    interests = models.CharField(verbose_name='Интересы', null=True, max_length=200)

    is_staff = models.BooleanField(verbose_name='Персонал?', default=False)
    is_active = models.BooleanField(verbose_name='Активен?', default=True)
    date_joined = models.DateTimeField(verbose_name='Дата регистрации', auto_now_add=True)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def get_full_name(self):
        return self.name
        pass

    def get_short_name(self):
        return self.email

