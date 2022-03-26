from django.urls import path
from .views import index, detail, RegisterUserView, RegisterDoneView, LogoutView, ChangeUserInfoView

app_name = 'main'
urlpatterns = [
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile_change'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/login/', login, name='login'),
    path('films/<int:pk>/', detail, name='detail'),
    path('', index, name='index'),
]
