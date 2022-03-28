from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

import string
import random


class Movie(models.Model):
    movie_title = models.CharField(max_length=200, verbose_name='Название')
    movie_image = models.ImageField(upload_to='movieImgs/', default='movieImgs/default.png', verbose_name='Изображение')
    movie_country = models.CharField(max_length=100, verbose_name='Страна')
    movie_year = models.CharField(max_length=10, verbose_name='Год')
    movie_duration = models.IntegerField(verbose_name='Продолжительность')
    movie_description = models.TextField(max_length=2000, verbose_name='Описание')
    movie_genres = models.ManyToManyField('Genre', verbose_name='Жанры')

    def __str__(self):
        return self.movie_title

    def get_genres_str(self):
        return ', '.join(g.genre_name for g in self.movie_genres.all())

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
        ordering = ['genre_name']


class MovieSession(models.Model):
    session_movie = models.ForeignKey(Movie, on_delete=models.PROTECT, verbose_name='Сеанс фильма')
    session_date = models.DateTimeField(verbose_name='Дата и время')
    session_price = models.FloatField(default=1, verbose_name='Цена')
    # session_seats = models.ForeignKey("Seats", on_delete=models.PROTECT, verbose_name='Места')
    # session_bookings = models.ManyToManyField("Booking", verbose_name='Бронирования')

    def __str__(self):
        return '{} {}'.format(self.session_movie, self.session_date)

    def get_booked_seats(self):
        """

        :return: list with booked seats
        """
        q = Q(booking_status__status_name='Подтвержден')
        return [seat.seats_number for b_obj in self.booking_set.filter(q) for seat in b_obj.booking_seats.all()]

    class Meta:
        verbose_name = 'Сеанс'
        verbose_name_plural = 'Сеансы'


class Booking(models.Model):
    booking_owner = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Владелец бронирования')
    booking_code = models.CharField(max_length=50, verbose_name='Уникальный код бронирования', default='')
    booking_payment = models.ForeignKey('Payment', on_delete=models.PROTECT, verbose_name='Оплата', null=True)
    booking_seats = models.ManyToManyField("Seats", verbose_name='Бронируемые места')
    booking_session = models.ForeignKey(MovieSession, on_delete=models.PROTECT, verbose_name='Сеанс', default='0')
    booking_status = models.ForeignKey('Status', on_delete=models.PROTECT, verbose_name='Статус')
    booking_description = models.CharField(max_length=200, verbose_name='Примечания', null=True, blank=True)
    booking_date = models.DateTimeField(verbose_name='Дата и время бронирования')

    def __str__(self):
        return '{} {}'.format(self.booking_owner, self.booking_date)

    def get_seats(self):
        return ", ".join([str(s.seats_number) for s in self.booking_seats.all()])

    def save(self, *args, **kwargs):
        size = 18
        chars = string.ascii_uppercase + string.digits
        self.booking_code = ''.join(random.choice(chars) for _ in range(size))

        super(Booking, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'


class Seats(models.Model):
    seats_number = models.IntegerField(verbose_name='Номер места')

    def __str__(self):
        return str(self.seats_number)

    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'Места'
        ordering = ['seats_number']


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
