from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta


def default_expire_date():
    """По умолчанию опрос живёт 7 дней."""
    return timezone.now() + timedelta(days=7)


class Question(models.Model):
    """Модель опроса (вопрос)."""
    question_text = models.CharField("Текст вопроса", max_length=255)
    pub_date = models.DateTimeField("Дата создания", default=timezone.now)
    expire_at = models.DateTimeField("Действителен до", default=default_expire_date)
    image = models.ImageField("Изображение (опционально)", upload_to="polls/images/", blank=True, null=True)

    # Кто предложил опрос (опционально)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="proposed_questions",
        verbose_name="Кем предложен"
    )

    # Только после одобрения админом опрос появляется на главной
    is_approved = models.BooleanField("Одобрен админом", default=False)

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.question_text

    def is_active(self):
        """Возвращает True, если сейчас опрос активен (не просрочен)."""
        if self.expire_at is None:
            return True
        return timezone.now() < self.expire_at

    def total_votes(self):
        """Общее количество голосов по всем вариантам этого вопроса."""
        return Vote.objects.filter(choice__question=self).count()


class Choice(models.Model):
    """Вариант ответа для вопроса."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    choice_text = models.CharField("Текст варианта", max_length=255)

    def __str__(self):
        # полезно в админке
        return f"{self.choice_text} ({self.question.question_text})"

    def votes_count(self):
        return self.votes.count()


class Vote(models.Model):
    """Голос пользователя. Ограничение: один голос пользователя на вопрос."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="votes")
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name="votes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # уникальность не по choice, а по (user, choice.question) — enforce via save()
        indexes = [
            models.Index(fields=["user"], name="vote_user_idx"),
        ]

    def save(self, *args, **kwargs):
        # защита: пользователь не может иметь >1 голос на один вопрос
        question = self.choice.question
        existing = Vote.objects.filter(user=self.user, choice__question=question).exclude(pk=self.pk)
        if existing.exists():
            raise ValueError("Пользователь уже голосовал в этом вопросе")
        super().save(*args, **kwargs)
