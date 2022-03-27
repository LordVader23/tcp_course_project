from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView, PasswordChangeView
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404


from django.core.paginator import Paginator

from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, DeleteView

from .models import MovieSession, Booking
from .forms import FilterForm, RegisterUserForm, ChangeInfoForm, LoginUserForm


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

# Auth views --------------------------------------------------------------


class RegisterUserView(CreateView):
    model = User
    template_name = 'main/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('main:register_done')


class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'


def login(request, template_name='registration/login.html',
          authentication_form=LoginUserForm):
    if request.method == 'POST':
        form = LoginUserForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data['remember_me']
            user = authenticate(username=username, password=password)

            if user:
                auth_login(request, user)

                if not remember_me:
                    context = {'form': form}
                    response = render(request, 'main/login.html', context)

                    # keys = [key for key in request.session.keys()]
                    # request.session[keys[0]].set_expiry(0)
                    # ['_auth_user_id', '_auth_user_backend', '_auth_user_hash']
                    # request.session['_auth_user_id'].set_expiry(0)
                    request.session.set_expiry(0)

                    # settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = True

                    return HttpResponseRedirect(reverse_lazy('main:index'))
                else:
                    return HttpResponseRedirect(reverse_lazy('main:profile'))
            else:
                form = LoginUserForm()
                context = {'form': form}

                return render(request, 'main/login.html', context)
        else:
            form = LoginUserForm()
            context = {'form': form}

            return render(request, 'main/login.html', context)
    else:
        form = LoginUserForm()
        context = {'form': form}

        return render(request, 'main/login.html', context)


# Profile views -----------------------------------------------------------------------
@login_required
def profile(request):
    bookings = Booking.objects.filter(booking_owner=request.user.pk)
    context = {'bookings': bookings}

    return render(request, 'main/profile.html', context)


class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'main/change_user_info.html'
    form_class = ChangeInfoForm
    success_url = reverse_lazy('main:profile')
    success_message = 'Личные данные пользователя изменены'

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'main/delete_user.html'
    success_url = reverse_lazy('main:index')

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удален')
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class PasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'main/password_change.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Пароль пользователя изменен'
