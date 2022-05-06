from django.contrib.auth import authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView, PasswordChangeView
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404


from django.core.paginator import Paginator

from django.db.models import Q
from django.db import connection
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, DeleteView

from .models import MovieSession, Booking, Seats, Status, Payment
from .forms import FilterForm, RegisterUserForm, ChangeInfoForm, LoginUserForm, BookingForm

from datetime import datetime


def index(request):
    mss = MovieSession.objects.all().exclude(session_date__lte=datetime.now()).order_by('-session_date')
    initial = {}  # To initialize form
    get_copy = request.GET.copy()

    for param in get_copy:  # To filter articles
        if param in request.GET:
            if request.GET[param]:
                if param == 'keyword':
                    keyword = request.GET['keyword']
                    q = Q(session_movie__movie_title__icontains=keyword)
                    mss = mss.filter(q)
                    initial['keyword'] = keyword
                elif param == 'date':  # To find out if price_from bigger(or equal) than price_to
                    date = request.GET['date']
                    date_list = date.split('-')
                    mss = mss.filter(session_date__year=date_list[0],
                                     session_date__month=date_list[1],
                                     session_date__day=date_list[2])
                    initial['date'] = date
                elif param == 'genre':
                    genre = request.GET['genre']
                    mss = mss.filter(session_movie__movie_genres=genre)
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
    num_pages = paginator.num_pages

    context = {'mss': mss, 'page': page, 'form': form,
               'num_pages': num_pages, 'num_pages_range': range(1, num_pages + 1)}

    return render(request, 'main/index.html', context)


def detail(request, pk):
    ms = get_object_or_404(MovieSession, pk=pk)
    form = BookingForm()

    if request.POST and request.user.is_authenticated:
        if request.POST.get('seats'):
            form = BookingForm(request.POST)
            if form.is_valid():
                seats_l = [int(i) for i in form.cleaned_data.get('seats')]
                status = Status.objects.filter(Q(status_name='Новый'))[0]

                if request.POST.get('description'):
                    b = Booking(booking_owner=request.user, booking_session=ms, booking_status=status,
                                booking_description=request.POST.get('description'), booking_date=datetime.now())
                    b.save()
                else:
                    b = Booking(booking_owner=request.user, booking_session=ms,
                                booking_status=status, booking_date=datetime.now())
                    b.save()

                # adding seats
                for seat in seats_l:
                    seat_obj = Seats(seats_number=seat)
                    seat_obj.save()
                    b.booking_seats.add(seat_obj)

                return HttpResponseRedirect(reverse_lazy('main:profile'))

    seats = [[1, 2, 3, 4, 5, 6, 7], [8, 9, 10, 11, 12, 13, 14], [15, 16, 17, 18, 19, 20, 21],
             [22, 23, 24, 25, 26, 27], [28, 29, 30, 31, 32, 33]]
    b_seats = ms.get_booked_seats()

    if len(b_seats) == 33:
        all_booked = True
    else:
        all_booked = False

    context = {'ms': ms, 'form': form, 'seats': seats, 'b_seats': b_seats, 'all_booked': all_booked}

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
                    request.session.set_expiry(0)

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

    for b in bookings:
        if b.booking_payment is None or not b.booking_payment.payment_is_done:
            diff = b.booking_session.session_date.replace(tzinfo=None) - datetime.now()
            diff = int(diff.total_seconds())
            if diff < 0 or (diff / 60) < 60:
                b.booking_status = Status.objects.get(status_name='Отменен')
                b.save()

    context = {'bookings': bookings}

    if 'cancel_booking_submit' in request.POST:
        if request.POST.get('booking_pk'):
            pk = int(request.POST.get('booking_pk'))
            b = get_object_or_404(Booking, pk=pk)
            b.delete()

            bookings = Booking.objects.filter(booking_owner=request.user.pk)
            context = {'bookings': bookings}

            return render(request, 'main/profile.html', context)

    if 'delete_user_submit' in request.POST:
        request.user.delete()

        return redirect('index')

    if 'change_password_submit' in request.POST:
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('index')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)

    context['form'] = form

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


def payment(request, pk):
    context = {}
    b = get_object_or_404(Booking, pk=pk)
    price_sum = b.booking_session.session_price * len(b.booking_seats.all())

    if request.method == 'POST':
        if 'payment_submit' in request.POST:
            p = Payment(payment_is_done=True, payment_date=datetime.now(), payment_info=f'Booking pk = {pk}')
            p.save()

            b.booking_payment = p
            b.save()

            return redirect('main:profile')

    context['price_sum'] = price_sum

    return render(request, 'main/payment.html', context)
