from django.urls import path
from .views import index, detail

app_name = 'main'
urlpatterns = [
    path('films/<int:pk>/', detail, name='detail'),
    path('', index, name='index'),
]
