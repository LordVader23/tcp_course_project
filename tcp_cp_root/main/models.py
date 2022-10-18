from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser

import string
import random

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.


class Booking(models.Model):
    booking_id = models.AutoField(primary_key=True)
    date = models.DateTimeField(verbose_name='Дата')
    code = models.CharField(max_length=50, verbose_name='Код')
    user = models.ForeignKey('Users', models.CASCADE, verbose_name='Пользователь')
    payment = models.ForeignKey('Payment', models.DO_NOTHING, blank=True, null=True, verbose_name='Оплата')
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name='Описание')
    session = models.ForeignKey('Moviesession', models.CASCADE, verbose_name='Сеанс')
    status = models.ForeignKey('Status', models.CASCADE, verbose_name='Статус')
    seats = models.ManyToManyField("Seats", verbose_name='Бронируемые места')

    def __str__(self):
        return f'User {self.user.username} on date {self.date}'

    def get_seats(self):
        return ", ".join([str(s.seat_number) for s in self.seats.all()])

    def get_amount_seats(self):
        return len(self.seats.all())

    def save(self, *args, **kwargs):
        size = 18
        chars = string.ascii_uppercase + string.digits
        self.code = ''.join(random.choice(chars) for _ in range(size))

        super(Booking, self).save(*args, **kwargs)

    class Meta:
        managed = False
        db_table = 'booking'
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-date']


class BookingSeats(models.Model):
    seat = models.OneToOneField('Seats', models.DO_NOTHING, primary_key=True, verbose_name='Место')
    booking = models.ForeignKey(Booking, models.DO_NOTHING, verbose_name='Бронирование')

    class Meta:
        managed = False
        db_table = 'booking_seats'
        unique_together = (('seat', 'booking'),)


class Cinema(models.Model):
    cinema_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name='Название')
    rate = models.FloatField(verbose_name='Рейтинг')
    despription = models.TextField(blank=True, null=True, verbose_name='Описание')
    city = models.ForeignKey('City', models.CASCADE, verbose_name='Город')

    def __str__(self):
        return f'{self.name} - {self.city.name}'

    class Meta:
        managed = False
        db_table = 'cinema'
        verbose_name = 'Кинотеатр'
        verbose_name_plural = 'Кинотеатры'


class City(models.Model):
    city_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name='Город')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        managed = False
        db_table = 'city'
        verbose_name = 'Город'
        verbose_name_plural = 'Город'


class Genres(models.Model):
    genre_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, verbose_name='Название')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        managed = False
        db_table = 'genres'
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['title']


class Movie(models.Model):
    movie_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, verbose_name='Название')
    country = models.CharField(max_length=100, verbose_name='Страна')
    year = models.CharField(max_length=10, verbose_name='Год')
    duration = models.IntegerField(verbose_name='Продолжительность')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    image = models.ImageField(upload_to='movieImgs/', default='movieImgs/default.png', verbose_name='Изображение')
    rate = models.FloatField(verbose_name='Рейтинг')
    movie_genres = models.ManyToManyField('Genres', verbose_name='Жанры')

    def __str__(self):
        return f'{self.title}'

    def get_genres_str(self):
        return ', '.join(g.name for g in self.movie_genres.all())

    class Meta:
        managed = True
        db_table = 'movie'
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'


class MovieGenre(models.Model):
    movie = models.OneToOneField(Movie, models.DO_NOTHING, primary_key=True, verbose_name='Фильм')
    genre = models.ForeignKey(Genres, models.DO_NOTHING, verbose_name='Жанр')

    def __str__(self):
        return 'Movie {} - genre {}'.format(self.movie.title, self.genre.title)

    class Meta:
        managed = False
        db_table = 'movie_genre'
        unique_together = (('movie', 'genre'),)


class Moviesession(models.Model):
    session_id = models.AutoField(primary_key=True)
    date = models.DateTimeField(verbose_name='Дата')
    price = models.FloatField(verbose_name='Цена')
    movie = models.ForeignKey(Movie, models.CASCADE, verbose_name='Фильм')
    cinema = models.ForeignKey(Cinema, models.DO_NOTHING, verbose_name='Кинотеатр')
    comment = models.CharField(max_length=200, blank=True, null=True, verbose_name='Комментарий')

    def get_booked_seats(self):
        """

        :return: list with booked seats
        """
        q = Q(booking_status__status_name='Подтвержден')
        return [seat.seat_number for b_obj in self.booking_set.filter(q) for seat in b_obj.seats.all()]

    def __str__(self):
        return 'Session {} on {}'.format(self.movie.title, self.date)

    class Meta:
        managed = False
        db_table = 'moviesession'
        verbose_name = 'Сеанс'
        verbose_name_plural = 'Сеансы'
        ordering = ['-date']


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    date = models.DateTimeField(verbose_name='Дата')
    is_done = models.IntegerField(verbose_name='Проведен')

    def __str__(self):
        return 'payment {} with date {}'.format(self.payment_id, self.date)

    class Meta:
        managed = False
        db_table = 'payment'
        verbose_name = 'Оплата'
        verbose_name_plural = 'Оплаты'


class Seats(models.Model):
    seat_id = models.AutoField(primary_key=True)
    seat_number = models.IntegerField(verbose_name='Номер места')

    def __str__(self):
        return self.seat_number

    class Meta:
        managed = False
        db_table = 'seats'
        verbose_name = 'Место'
        verbose_name_plural = 'Места'


class Status(models.Model):
    status_id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=100, verbose_name='Статус')

    def __str__(self):
        return self.status_name

    class Meta:
        managed = False
        db_table = 'status'
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'


class Users(AbstractUser):
    # user_id = models.AutoField(primary_key=True)
    # username = models.CharField(max_length=100)
    # email = models.CharField(max_length=100)
    # password = models.CharField(max_length=100)
    # first_name = models.CharField(max_length=100, blank=True, null=True)
    # last_name = models.CharField(max_length=100, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True, verbose_name='Дата рождения')

    def __str__(self):
        return self.username

    class Meta:
        managed = True
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
