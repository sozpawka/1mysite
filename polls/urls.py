# polls/urls.py
from django.urls import path
from . import views

app_name = "polls"

urlpatterns = [
    path("", views.index, name="index"),
    path("question/<int:pk>/", views.detail, name="detail"),
    path("question/<int:pk>/vote/", views.vote, name="vote"),
    path("propose/", views.propose_question, name="propose_question"),
    path("proposed/", views.proposed_list, name="proposed_list"),
]
