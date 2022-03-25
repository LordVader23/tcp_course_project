from django.shortcuts import render
from django.shortcuts import get_object_or_404

from django.core.paginator import Paginator

from .models import MovieSession


def index(request):
    mss = MovieSession.objects.all()  # change to raw sql later!!!

    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1

    paginator = Paginator(mss, 7)
    page = paginator.get_page(page_num)

    context = {'mss': mss, 'page': page}

    return render(request, 'main/index.html', context)


def detail(request, pk):
    ms = get_object_or_404(MovieSession, pk=pk)

