from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.contrib import messages

from .models import Question, Choice, Vote
from .forms import QuestionProposalForm, ChoiceForm


def index(request):
    """Главная: показываем только одобренные и активные опросы."""
    # staff (админ) может видеть все опросы на специальной странице через админку
    qs = Question.objects.filter(is_approved=True, pub_date__lte=timezone.now())
    # показываем только активные (expire_at > now) или те, у которых expire_at пусто
    qs = qs.filter(expire_at__gt=timezone.now())
    return render(request, "polls/index.html", {"questions": qs})


def detail(request, pk):
    """
    Детальная страница опроса.
    Если пользователь уже голосовал — показываем его выбор и результаты (а не форму).
    """
    question = get_object_or_404(Question, pk=pk)

    # если опрос не одобрен и пользователь не staff — показываем сообщение/404-like
    if not question.is_approved and not (request.user.is_authenticated and request.user.is_staff):
        return render(request, "polls/forbidden.html", {"message": "Этот опрос пока не опубликован."})

    # проверка голосовал ли юзер
    user_voted = False
    user_choice = None
    if request.user.is_authenticated:
        vote = Vote.objects.filter(user=request.user, choice__question=question).first()
        if vote:
            user_voted = True
            user_choice = vote.choice

    # подсчёт результатов: подготовим список (choice, votes, percent)
    choices = []
    total = question.total_votes()
    for ch in question.choices.all():
        votes = ch.votes_count()
        pct = (votes / total * 100) if total > 0 else 0
        choices.append({"choice": ch, "votes": votes, "percent": round(pct, 2)})

    context = {
        "question": question,
        "user_voted": user_voted,
        "user_choice": user_choice,
        "results": choices,
        "total_votes": total,
    }
    return render(request, "polls/detail.html", context)


@login_required
def vote(request, pk):
    question = get_object_or_404(Question, pk=pk)

    # запрет голосования если опрос просрочен или не одобрен (для обычных пользователей)
    if not question.is_active() or (not question.is_approved and not request.user.is_staff):
        messages.error(request, "Голосование закрыто.")
        return redirect("polls:detail", pk=pk)

    # проверяем, есть ли уже голос от пользователя
    if Vote.objects.filter(user=request.user, choice__question=question).exists():
        messages.info(request, "Вы уже голосовали в этом опросе.")
        return redirect("polls:detail", pk=pk)

    if request.method == "POST":
        choice_id = request.POST.get("choice")
        if not choice_id:
            messages.error(request, "Выберите вариант.")
            return redirect("polls:detail", pk=pk)
        choice = get_object_or_404(Choice, pk=choice_id, question=question)
        try:
            Vote.objects.create(user=request.user, choice=choice)
            messages.success(request, "Спасибо — ваш голос учтён.")
        except Exception as exc:
            messages.error(request, f"Не удалось сохранить голос: {exc}")
        return redirect("polls:detail", pk=pk)

    return redirect("polls:detail", pk=pk)


@login_required
def propose_question(request):
    """
    Пользователь предлагает новый опрос.
    По умолчанию is_approved=False — админ должен одобрить.
    """
    # форма для создания вариантов: минимум 2
    ChoiceFormSet = inlineformset_factory(Question, Choice, form=ChoiceForm, extra=2, min_num=2, validate_min=True)

    if request.method == "POST":
        q_form = QuestionProposalForm(request.POST, request.FILES)
        if q_form.is_valid():
            # создаём объект, но не сохраняем сразу (чтобы привязать created_by)
            question = q_form.save(commit=False)
            question.created_by = request.user
            question.is_approved = False
            question.save()
            formset = ChoiceFormSet(request.POST, instance=question)
            if formset.is_valid():
                formset.save()
                messages.success(request, "Опрос отправлен на рассмотрение. После одобрения он появится на главной.")
                return redirect("polls:proposed_list")
            else:
                # если formset не валиден — удаляем незавершённый вопрос чтобы не оставлять пустышку
                question.delete()
        else:
            formset = ChoiceFormSet(request.POST)
    else:
        q_form = QuestionProposalForm()
        formset = ChoiceFormSet()

    return render(request, "polls/propose.html", {"q_form": q_form, "formset": formset})


@login_required
def proposed_list(request):
    """Список предложенных пользователем опросов (его собственных)."""
    qs = Question.objects.filter(created_by=request.user).order_by("-pub_date")
    return render(request, "polls/proposed_list.html", {"questions": qs})
