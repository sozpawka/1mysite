from django.contrib import admin
from .models import Question, Choice


@admin.action(description="Отметить как одобренные")
def make_approved(modeladmin, request, queryset):
    queryset.update(is_approved=True)


@admin.action(description="Отменить одобрение")
def make_unapproved(modeladmin, request, queryset):
    queryset.update(is_approved=False)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text", "created_by", "pub_date", "expire_at", "is_approved")
    list_filter = ("is_approved", "pub_date")
    actions = [make_approved, make_unapproved]
    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("choice_text", "question")
