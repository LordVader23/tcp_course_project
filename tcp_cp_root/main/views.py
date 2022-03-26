from django.shortcuts import render
from django.shortcuts import get_object_or_404

from django.core.paginator import Paginator

from django.db.models import Q

from .models import MovieSession
from .forms import FilterForm


def index(request):
    mss = MovieSession.objects.all()  # change to raw sql later!!!
    initial = {}  # To initialize form

    get_copy = request.GET.copy()

    for param in get_copy:  # To filter articles
        if param in request.GET:
            if request.GET[param]:
                if param == 'keyword':
                    keyword = request.GET['keyword']
                    q = Q(session_movie__movie_title__icontains=keyword)
                    mss = mss.filter(q)  # change to raw sql later!!!
                    initial['keyword'] = keyword
                elif param == 'date':  # To find out if price_from bigger(or equal) than price_to
                    date = request.GET['date']
                    date_list = date.split('-')
                    mss = mss.filter(session_date__year=date_list[0],
                                     session_date__month=date_list[1],
                                     session_date__day=date_list[2])  # change to raw sql later!!!
                    initial['date'] = date
                elif param == 'genre':
                    genre = request.GET['genre']
                    mss = mss.filter(session_movie__movie_genres=genre)  # change to raw sql later!!!
                    initial['genre'] = genre

    if len(initial) > 0:
        form = FilterForm(initial=initial)
    else:
        form = FilterForm()

    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1

    paginator = Paginator(mss, 7)
    page = paginator.get_page(page_num)

    context = {'mss': mss, 'page': page, 'form': form}

    return render(request, 'main/index.html', context)


def detail(request, pk):
    ms = get_object_or_404(MovieSession, pk=pk)  # change to raw sql later!!!
    form = ''
    # need form for booking

    context = {'ms': ms, 'form': form}

    return render(request, 'main/detail.html', context)
