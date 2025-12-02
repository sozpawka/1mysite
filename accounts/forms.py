from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()


class RegisterForm(UserCreationForm):
    """
    Форма регистрации. Добавлено поле email и поле photo для загрузки аватара.
    """
    email = forms.EmailField(required=True)
    photo = forms.ImageField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "photo")

    def save(self, commit=True):
        user = super().save(commit=commit)
        # Сохраняем профиль с фото (если есть)
        photo = self.cleaned_data.get("photo")
        if commit:
            # создаем профиль если его нет или обновляем
            profile, created = Profile.objects.get_or_create(user=user)
            if photo:
                profile.photo = photo
                profile.save()
        else:
            # если commit=False, не сохраняем профиль сейчас
            pass
        return user


class ProfileForm(forms.ModelForm):
    """Форма редактирования профиля."""
    class Meta:
        model = Profile
        fields = ["full_name", "photo", "bio"]
