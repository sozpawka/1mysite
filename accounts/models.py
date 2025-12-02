from django.db import models
from django.conf import settings
from django.dispatch import receiver


def user_photo_upload_to(instance, filename):
    """
    Функция, которая формирует путь для сохранения фото пользователя.
    Используется в поле Profile.photo.
    """
    return f"avatars/user_{instance.user.id}/{filename}"


def user_avatar_path(instance, filename):
    return user_photo_upload_to(instance, filename)


class Profile(models.Model):
    """Профиль пользователя."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    full_name = models.CharField("Имя", max_length=150, blank=True)
    photo = models.ImageField("Фото профиля", upload_to=user_photo_upload_to, blank=True, null=True)
    bio = models.TextField("О себе", blank=True)

    def __str__(self):
        return self.full_name or self.user.username


# При удалении профиля удаляем файл с диска (если он есть)
@receiver(models.signals.post_delete, sender=Profile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.photo:
        try:
            instance.photo.delete(save=False)
        except Exception:
            pass
