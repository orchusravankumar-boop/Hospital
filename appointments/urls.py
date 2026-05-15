from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.appointment_page,
        name='appointment_page'
    ),

    path(
        'confirm-appointment/',
        views.confirm_appointment,
        name='confirm_appointment'
    ),

    path(
        'gemini-test/',
        views.gemini_test,
        name='gemini_test'
    ),

]
