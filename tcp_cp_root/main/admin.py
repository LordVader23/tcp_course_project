from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Genre, Status, Seats, Movie, Payment, Booking, MovieSession


class MovieAdm(admin.ModelAdmin):
    list_display = ('movie_title', 'movie_country', 'movie_year', 'movie_duration', 'get_genres', 'get_img')
    list_display_links = ('movie_title',)
    fields = ('movie_title', 'movie_country', 'movie_year', 'movie_duration',
              'movie_description', 'movie_genres', 'movie_image', 'get_img')
    readonly_fields = ('get_img',)
    search_fields = ('id', 'movie_title', 'movie_country')
    list_filter = ('movie_year', 'movie_genres')
    list_per_page = 10
    list_max_show_all = 100

    #     movie_title
    #     movie_image
    #     movie_country
    #     movie_year
    #     movie_duration
    #     movie_description
    #     movie_genres

    def get_genres(self, obj):
        return "\n".join([g.genre_name for g in obj.movie_genres.all()])

    def get_img(self, obj):
        if obj.movie_image:
            return mark_safe(f'<img src="{obj.movie_image.url}" width="120px"')
        else:
            return 'нет картинки'

    get_img.short_description = 'Предпросмотр фото'
    get_genres.short_description = 'Жанры'


class BookingAdm(admin.ModelAdmin):
    list_display = ('booking_owner', 'booking_session', 'booking_status',  'booking_code', 'booking_payment',
                    'get_seats', 'booking_description', 'booking_date')
    list_display_links = ('booking_owner', )
    fields = ('booking_owner', 'booking_session', 'booking_status',
              'booking_seats', 'booking_description', 'booking_date')
    readonly_fields = ('get_seats',)
    search_fields = ('booking_date', )
    list_filter = ('booking_status', )
    list_editable = ('booking_status',)
    list_per_page = 10
    list_max_show_all = 100

    def get_seats(self, obj):
        return ", ".join([str(s.seats_number) for s in obj.booking_seats.all()])

    get_seats.short_description = 'Места'

    # booking_owner
    # booking_code
    # booking_payment
    # booking_seats
    # booking_session
    # booking_status
    # booking_description
    # booking_date


class MovieSessionAdm(admin.ModelAdmin):
    list_display = ('session_movie', 'session_date', 'session_price', 'get_booked_seats')
    list_display_links = ('session_movie',)
    fields = ('session_movie', 'session_date', 'session_price')
    list_filter = ('session_movie', 'session_date')
    list_per_page = 10
    list_max_show_all = 100

    def get_booked_seats(self, obj):
        return ", ".join([str(s) for s in obj.get_booked_seats()])

    get_booked_seats.short_description = 'Забронированные места'


admin.site.register(Movie, MovieAdm)
admin.site.register(Booking, BookingAdm)
admin.site.register(MovieSession, MovieSessionAdm)
admin.site.register(Genre)
admin.site.register(Status)
admin.site.register(Payment)
