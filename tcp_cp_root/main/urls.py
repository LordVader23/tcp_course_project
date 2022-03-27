from django.urls import path
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView
from .views import index, detail
from .views import RegisterUserView, RegisterDoneView, login
from .views import profile, DeleteUserView, ChangeUserInfoView, PasswordChangeView

app_name = 'main'
urlpatterns = [
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('accounts/profile/delete/', DeleteUserView.as_view(), name='profile_delete'),
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile_change'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/password/reset/', login, name='password_reset'),
    path('accounts/login/', login, name='login'),
    path('accounts/password/change/', PasswordChangeView.as_view(), name='password_change'),
    path('films/<int:pk>/', detail, name='detail'),
    path('', index, name='index'),
]
