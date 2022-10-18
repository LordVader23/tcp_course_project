from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Genres, Status, Seats, Movie, Payment, Booking, Moviesession


class MovieAdm(admin.ModelAdmin):
    list_display = ('title', 'country', 'year', 'duration', 'get_genres', 'get_img')
    list_display_links = ('title',)
    fields = ('title', 'country', 'year', 'duration',
              'description', 'movie_genres', 'image', 'get_img')
    readonly_fields = ('get_img',)
    search_fields = ('movie_id', 'title', 'country')
    list_filter = ('year', 'movie_genres')
    list_per_page = 10
    list_max_show_all = 100

    def get_genres(self, obj):
        return "\n".join([g.name for g in obj.movie_genres.all()])

    def get_img(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="120px"')
        else:
            return 'нет картинки'

    get_img.short_description = 'Предпросмотр фото'
    get_genres.short_description = 'Жанры'


class BookingAdm(admin.ModelAdmin):
    list_display = ('user', 'session', 'status',  'code', 'payment', 'get_seats', 'description', 'date')
    list_display_links = ('user', )
    fields = ('user', 'session', 'status', 'seats', 'description', 'date')
    readonly_fields = ('get_seats',)
    search_fields = ('date', )
    list_filter = ('status', )
    list_editable = ('status',)
    list_per_page = 10
    list_max_show_all = 100

    def get_seats(self, obj):
        return ", ".join([str(s.seat_number) for s in obj.seats.all()])

    get_seats.short_description = 'Места'


class MovieSessionAdm(admin.ModelAdmin):
    list_display = ('movie', 'date', 'price', 'get_booked_seats')
    list_display_links = ('movie',)
    fields = ('movie', 'date', 'price')
    list_filter = ('movie', 'date')
    list_per_page = 10
    list_max_show_all = 100

    def get_booked_seats(self, obj):
        return ", ".join([str(s) for s in obj.get_booked_seats()])

    get_booked_seats.short_description = 'Забронированные места'


admin.site.register(Movie, MovieAdm)
admin.site.register(Booking, BookingAdm)
admin.site.register(Moviesession, MovieSessionAdm)
admin.site.register(Genres)
admin.site.register(Status)
admin.site.register(Payment)
