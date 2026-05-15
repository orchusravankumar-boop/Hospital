from django.urls import path
from .views import ai_chat

urlpatterns = [
    path('ai/', ai_chat, name='ai_chat'),
]