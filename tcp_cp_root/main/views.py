from django.contrib.auth import authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView, PasswordChangeView
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db.models.expressions import RawSQL
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404


from django.core.paginator import Paginator

from django.db.models import Q
from django.db import connection
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, DeleteView

from .models import MovieSession, Booking, Seats, Status, Payment, Genre
from .forms import FilterForm, RegisterUserForm, ChangeInfoForm, LoginUserForm, BookingForm

from datetime import datetime
import datetime as just_datetime

import random
import string


# SQLs
# Index SQLs
SQL1 = f"SELECT * FROM `main_moviesession` WHERE session_date > '{str(datetime.now())}' ORDER BY `main_moviesession`.`session_date` DESC;"
SQL2 = "SELECT main_moviesession.id, main_moviesession.session_movie_id, main_moviesession.session_date, main_moviesession.session_price FROM main_moviesession INNER JOIN main_movie ON (main_moviesession.session_movie_id = main_movie.id) WHERE main_movie.movie_title LIKE '%%{}%%'"
SQL3 = "SELECT * FROM `main_moviesession` WHERE (NOT (`main_moviesession`.`session_date` <= '{now}') AND `main_moviesession`.`session_date` BETWEEN '{min}' AND '{max}') ORDER BY `main_moviesession`.`session_date` DESC"
SQL4 = "SELECT * FROM `main_moviesession` INNER JOIN `main_movie` ON (`main_moviesession`.`session_movie_id` = `main_movie`.`id`) INNER JOIN `main_movie_movie_genres` ON (`main_movie`.`id` = `main_movie_movie_genres`.`movie_id`) WHERE (NOT (`main_moviesession`.`session_date` <= '{now}') AND `main_movie_movie_genres`.`genre_id` = {genre_id}) ORDER BY `main_moviesession`.`session_date` DESC"
# Detail SQLs
SQL5 = "SELECT * FROM `main_moviesession` WHERE `main_moviesession`.`id` = {pk}"
SQL6 = "SELECT `main_status`.`id`, `main_status`.`status_name` FROM `main_status` WHERE `main_status`.`status_name` = '{status_name}'"
SQL7 = "INSERT INTO `main_booking` (`booking_owner_id`, `booking_code`, `booking_payment_id`, `booking_session_id`, `booking_status_id`, `booking_description`, `booking_date`) VALUES ({user_id}, '{code}', NULL, {session_id}, 2, {description}, '{now}')"
SQL8 = "INSERT INTO `main_seats` (`seats_number`) VALUES ({seat_num})"
# Profile SQLs
SQL9 = "SELECT * FROM `main_booking` WHERE `main_booking`.`booking_owner_id` = {user_id} ORDER BY `main_booking`.`booking_date` DESC"
SQL10 = "SELECT `main_status`.`id`, `main_status`.`status_name` FROM `main_status` WHERE `main_status`.`status_name` = '{status_name}'"
SQL11 = "DELETE FROM `main_booking` WHERE `main_booking`.`id` = {pk}"
# Payment SQLs
SQL12 = "SELECT * FROM `main_booking` WHERE `main_booking`.`booking_owner_id` = {user_id}, `main_booking`.`id` = {pk} ORDER BY `main_booking`.`booking_date` DESC"
SQL13 = "INSERT INTO `main_payment` (`payment_is_done`, `payment_date`, `payment_info`) VALUES (1, '{now}', 'Booking pk = {pk}')"


def index(request):
    mss = MovieSession.objects.raw(SQL1)
    initial = {}  # To initialize form

    get_copy = request.GET.copy()

    for param in get_copy:  # To filter articles
        if param in request.GET:
            if request.GET[param]:
                if param == 'keyword':
                    keyword = request.GET['keyword']
                    mss = MovieSession.objects.raw(SQL2.format(keyword))
                    initial['keyword'] = keyword
                elif param == 'date':  # To find out if price_from bigger(or equal) than price_to
                    date = request.GET['date']
                    date_list = date.split('-')
                    date_list = [int(i) for i in date_list]
                    dt_max = str(just_datetime.datetime(date_list[0], date_list[1], date_list[2], 23, 59, 59))
                    dt_min = str(just_datetime.datetime(date_list[0], date_list[1], date_list[2], 0, 0, 0))

                    mss = MovieSession.objects.raw(SQL3.format(now=str(datetime.now()), min=dt_min, max=dt_max))
                    initial['date'] = date
                elif param == 'genre':
                    genre = request.GET['genre']
                    mss = MovieSession.objects.raw(SQL4.format(now=str(datetime.now()), genre_id=int(genre)))
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
    ms = MovieSession.objects.raw(SQL5.format(pk=pk))
    if not ms:
        raise Http404

    ms = get_object_or_404(MovieSession, pk=pk)
    form = BookingForm()

    if request.POST and request.user.is_authenticated:
        if request.POST.get('seats'):
            form = BookingForm(request.POST)
            if form.is_valid():
                seats_l = [int(i) for i in form.cleaned_data.get('seats')]
                status = Status.objects.raw(SQL6.format(status_name='Новый'))

                status = Status.objects.filter(Q(status_name='Новый'))[0]
                if request.POST.get('description'):
                    size = 18
                    chars = string.ascii_uppercase + string.digits
                    code = ''.join(random.choice(chars) for _ in range(size))

                    b = Booking.objects.raw(SQL7.format(user_id=request.user.pk, code=code, session_id=pk,
                                                        description=request.POST.get('description'),
                                                        now=str(datetime.now())))
                    b = Booking(booking_owner=request.user, booking_session=ms, booking_status=status,
                                booking_description=request.POST.get('description'), booking_date=datetime.now())
                    b.save()
                else:
                    size = 18
                    chars = string.ascii_uppercase + string.digits
                    code = ''.join(random.choice(chars) for _ in range(size))

                    b = Booking.objects.raw(SQL7.format(user_id=request.user.pk, code=code, session_id=pk,
                                                        description='NULL', now=str(datetime.now())))
                    b = Booking(booking_owner=request.user, booking_session=ms,
                                booking_status=status, booking_date=datetime.now())
                    b.save()

                # adding seats
                for seat in seats_l:
                    seat_obj = Seats.objects.raw(SQL8.format(seat_num=seat))
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
    bookings = Booking.objects.raw(SQL9.format(user_id=request.user.pk))

    for b in bookings:
        if b.booking_payment is None or not b.booking_payment.payment_is_done:
            diff = b.booking_session.session_date.replace(tzinfo=None) - datetime.now()
            diff = int(diff.total_seconds())
            if diff < 0 or (diff / 60) < 60:
                status = Status.objects.raw(SQL10.format(status_name='Отменен'))
                b.booking_status = Status.objects.get(status_name='Отменен')
                b.save()

    context = {'bookings': bookings}

    if 'cancel_booking_submit' in request.POST:
        if request.POST.get('booking_pk'):
            pk = int(request.POST.get('booking_pk'))
            b = Booking.objects.raw(SQL11.format(pk=pk))
            b = get_object_or_404(Booking, pk=pk)
            b.delete()

            bookings = Booking.objects.raw(SQL9.format(user_id=request.user.pk))

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
    b = Booking.objects.raw(SQL12.format(user_id=request.user.pk, pk=pk))
    b = get_object_or_404(Booking, pk=pk)
    price_sum = b.booking_session.session_price * len(b.booking_seats.all())

    if request.method == 'POST':
        if 'payment_submit' in request.POST:
            p = Payment.objects.raw(SQL13.format(now=str(datetime.now()), pk=pk))
            p = Payment(payment_is_done=True, payment_date=datetime.now(), payment_info=f'Booking pk = {pk}')
            p.save()

            b.booking_payment = p
            b.save()

            return redirect('main:profile')

    context['price_sum'] = price_sum

    return render(request, 'main/payment.html', context)
