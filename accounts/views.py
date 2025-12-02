from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm, RegisterForm


@login_required
def profile_view(request):
    """
    Показываем профиль текущего пользователя.
    Если профиль ещё не создан — get_or_create его создаст.
    """
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён.')
            return redirect('accounts:profile_view')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def profile_delete(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.info(request, 'Ваш аккаунт был удалён.')
        return redirect('polls:index')
    return render(request, 'accounts/profile_delete.html')


def register(request):
    """
    Регистрация пользователя.
    Если форма регистрации содержит файл (аватар), нужно передавать request.FILES.
    После успешной регистрации создаём профиль (если форма не делает это сама).
    """
    if request.method == 'POST':
        # принимаем request.FILES, если форма регистрации имеет поле для фото
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            photo = form.cleaned_data.get('photo') if 'photo' in form.cleaned_data else None
            if photo:
                Profile.objects.create(user=user, photo=photo)
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('polls:index')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Вход пользователя — используем стандартную AuthenticationForm.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('polls:index')
        else:
            messages.error(request, 'Ошибка входа. Проверьте логин и пароль.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    Выход пользователя.
    """
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('polls:index')
