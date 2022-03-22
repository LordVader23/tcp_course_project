from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Genre, Status, Seats, Movie, MovieSession, Booking, Payment


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


admin.site.register(Movie, MovieAdm)
admin.site.register(Genre)
admin.site.register(Status)
# admin.site.register(Seats)
