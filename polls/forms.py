from django import forms
from .models import Question, Choice


class QuestionProposalForm(forms.ModelForm):
    """Форма для подачи нового предложения опроса."""
    class Meta:
        model = Question
        fields = ["question_text", "image", "expire_at"]
        widgets = {
            "expire_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class ChoiceForm(forms.ModelForm):
    """Форма для варианта ответа."""
    class Meta:
        model = Choice
        fields = ["choice_text"]
