from django import forms

from .models import Genre

from .widgets import DateInput


class FilterForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=20, label='Ключевое слово',
                              widget=forms.TextInput(attrs={'placeholder': 'Поиск'}))
    date = forms.DateField(required=False, label='Дата премьеры', widget=DateInput)
    genre = forms.ModelChoiceField(queryset=Genre.objects.all(), label='Жанр', required=False)
