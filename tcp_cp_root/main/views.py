from django.shortcuts import render

from django.core.paginator import Paginator

from .models import MovieSession


def index(request):
    mss = MovieSession.objects.all()  # change to raw sql later!!!

    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1

    paginator = Paginator(mss, 9)
    page = paginator.get_page(page_num)

    context = {'mss': mss, 'page': page}

    return render(request, 'main/index.html', context)


def detail(request, pk):
    pass
