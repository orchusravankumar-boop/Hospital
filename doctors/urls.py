from django.urls import path
from . import views

urlpatterns = [

    path('', views.doc_list),

    path('dashboard/', views.doctor_dashboard),

    path(
        'update-status/<int:appointment_id>/',
        views.update_status
    ),

]