from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from .models import Genres, Users, Cinema

from .widgets import DateInput


class FilterForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=20, label='Ключевое слово',
                              widget=forms.TextInput(attrs={'placeholder': 'Поиск'}))
    date = forms.DateField(required=False, label='Дата премьеры', widget=DateInput)
    genre = forms.ModelChoiceField(queryset=Genres.objects.all(), label='Жанр', required=False)
    cinema = forms.ModelChoiceField(queryset=Cinema.objects.all(), label='Кинотеатр', required=False)


class RegisterUserForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Адрес ел. почты')

    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Пароль(повторно)', widget=forms.PasswordInput,
                                help_text='Введите тот же пароль')

    def clean_password1(self):
        password1 = self.cleaned_data['password1']

        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        # password1 = password1.encode('utf-8').strip()
        password2 = self.cleaned_data['password2']
        # password2 = password1.encode('utf-8').strip()

        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError('Введенные пароли не совпадают', code='password_mismatch')}
            raise ValidationError(errors)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()

        return user

    class Meta:
        model = Users
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')


class LoginUserForm(forms.Form):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    remember_me = forms.BooleanField(label='Запомнить меня', required=False)


class ChangeInfoForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Адрес ел. почты')
    birthday = forms.DateField(label='Дата рождения')

    class Meta:
        model = Users
        fields = ('username', 'email', 'first_name', 'last_name')


class BookingForm(forms.Form):
    OPTIONS = (
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5"),
        ("6", "6"),
        ("7", "7"),
        ("8", "8"),
        ("9", "9"),
        ("10", "10"),
        ("11", "11"),
        ("12", "12"),
        ("13", "13"),
        ("14", "14"),
        ("15", "15"),
        ("16", "16"),
        ("17", "17"),
        ("18", "18"),
        ("19", "19"),
        ("20", "20"),
        ("21", "21"),
        ("22", "22"),
        ("23", "23"),
        ("24", "24"),
        ("25", "25"),
        ("26", "26"),
        ("27", "27"),
        ("28", "28"),
        ("29", "29"),
        ("30", "30"),
        ("31", "31"),
        ("32", "32"),
        ("33", "33"),
    )
    seats = forms.MultipleChoiceField(choices=OPTIONS)
    description = forms.CharField(widget=forms.Textarea, required=False, label='Примечание')
