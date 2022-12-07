from django.conf import settings
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date


# Create your models here.


class Genre(models.Model):
    name = models.CharField(
        max_length=200, help_text='Введите жанр книги',
        verbose_name='Жанр книги')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Language(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='Язык книги')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'Язык'
        verbose_name_plural = 'Языки'


class Author(models.Model):
    first_name = models.CharField(max_length=200, verbose_name='Имя автора')
    last_name = models.CharField(max_length=200, verbose_name='Фамилия автора')
    date_of_birth = models.DateField(
        verbose_name='Дата рождения', null=True, blank=True)
    date_of_death = models.DateField(
        verbose_name='Дата смерти', null=True, blank=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    class Meta:
        ordering = ('last_name', 'first_name')
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'


class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название книги")
    genre = models.ForeignKey(
        'Genre', on_delete=models.CASCADE, verbose_name='Жанр книги',
        null=True)
    language = models.ForeignKey(
        'Language', on_delete=models.CASCADE, verbose_name='Язык книги',
        null=True)
    author = models.ManyToManyField(
        'Author', verbose_name='Автор книги')
    summary = models.TextField(
        max_length=1000, verbose_name='Аннотация книги')
    isbn = models.CharField(
        max_length=13, verbose_name="ISBN",
        help_text='Должно содержать 13 символов')


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # return f"books/{self.id}"
        return reverse('book-detail', args=[str(self.id)])

    def display_author(self):
        return ', '.join([author.last_name for author in self.author.all()])

    display_author.short_description = 'Авторы'

    class Meta:
        ordering = ('title',)
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'


class Status(models.Model):
    name = models.CharField(
        max_length=20, verbose_name='Статус экземпляра книги')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'


class BookInstance(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE, null=True)
    inv_nom = models.CharField(max_length=20, verbose_name="Инвентарный номер")
    imprint = models.CharField(max_length=200, verbose_name="Издательство")
    status = models.ForeignKey(
        'Status', on_delete=models.CASCADE, null=True,
        verbose_name='Статус экземпляра книги')
    due_back = models.DateField(
        null=True, blank=True, verbose_name='Срок сдачи')
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 blank=True, verbose_name="Заказчик",
                                 help_text="Выберите заказчика книги")

    def __str__(self):
        return f"{self.inv_nom} {self.book} {self.status}"

    def get_status_display(self):
        return self.status

    class Meta:
        ordering = ('inv_nom',)
        verbose_name = 'Экземпляр книги'
        verbose_name_plural = 'Экземпляры книги'

    @property
    def is_overdue(self):
        return self.due_back and date.today() > self.due_back


RATING_CHOICES = ((1, "1"),
                  (2, "2"),
                  (3, "3"),
                  (4, "4"),
                  (5, "5"),
                  )


class Rating(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE, null=True)
    mark = models.IntegerField(choices=RATING_CHOICES, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.mark)
