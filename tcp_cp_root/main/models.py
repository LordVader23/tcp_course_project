from django.db import models
from django.contrib.auth.models import User


class Movie(models.Model):
    movie_title = models.CharField(max_length=200, verbose_name='Название')
    movie_image = models.ImageField(upload_to='movieImgs/', default='movieImgs/default.jpg', verbose_name='Изображение')
    movie_country = models.CharField(max_length=100, verbose_name='Страна')
    movie_year = models.CharField(max_length=10, verbose_name='Год')
    movie_duration = models.IntegerField(verbose_name='Продолжительность')
    movie_description = models.TextField(max_length=2000, verbose_name='Описание')
    movie_genres = models.ManyToManyField('Genre', verbose_name='Жанры')

    def __str__(self):
        return self.movie_title

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'


class Genre(models.Model):
    genre_name = models.CharField(max_length=100, verbose_name='Название жанра')

    def __str__(self):
        return self.genre_name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class MovieSession(models.Model):
    session_movie = models.ForeignKey(Movie, on_delete=models.PROTECT, verbose_name='Сеанс фильма')
    session_date = models.DateTimeField(verbose_name='Дата и время')
    # session_seats = models.ForeignKey("Seats", on_delete=models.PROTECT, verbose_name='Места')
    session_bookings = models.ManyToManyField("Booking", verbose_name='Бронирования')

    def __str__(self):
        return '{} {}'.format(self.session_movie, self.session_date)

    class Meta:
        verbose_name = 'Сеанс'
        verbose_name_plural = 'Сеансы'


class Booking(models.Model):
    booking_owner = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Владелец бронирования')
    booking_code = models.CharField(max_length=50, verbose_name='Уникальный код бронирования')
    booking_payment = models.ForeignKey('Payment', on_delete=models.PROTECT, verbose_name='Оплата')
    booking_seats = models.ManyToManyField("Seats", verbose_name='Бронируемые места')
    booking_status = models.ForeignKey('Status', on_delete=models.PROTECT, verbose_name='Статус')
    booking_description = models.CharField(max_length=200, verbose_name='Примечания')
    booking_date = models.DateTimeField(verbose_name='Дата и время бронирования')

    def __str__(self):
        return '{} {}'.format(self.booking_owner, self.booking_date)

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'


class Seats(models.Model):
    seats_number = models.IntegerField(verbose_name='Номер места')

    def __str__(self):
        return self.seats_number

    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'Места'


class Status(models.Model):
    status_name = models.CharField(max_length=200, verbose_name='Название статуса')

    def __str__(self):
        return self.status_name

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'


class Payment(models.Model):
    payment_is_done = models.BooleanField(verbose_name='Оплата завершена')
    payment_date = models.DateTimeField(auto_now=True, verbose_name='Время платежа')
    payment_info = models.CharField(max_length=100, verbose_name='Дополнительная информация')

    def __str__(self):
        return '{} {}'.format(self.payment_date, self.payment_is_done)

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
