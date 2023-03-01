from django.urls import path

from . import views

app_name = 'vaccines'

urlpatterns = [
    path('', views.vaccine_list, name='vaccine_list'),
    path('<int:vaccine_id>/', views.vaccine_detail, name='vaccine_detail'),
    path('<int:vaccine_id>/book-appointment/', views.book_appointment, name='book_appointment'),
    path('<int:vaccine_id>/book-appointment/<str:date>/', views.appointment_confirmation,
         name='appointment_confirmation'),

    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path('health-centers/', views.health_centers_list, name='health-centers'),
    path('health-centers/send_emai/<int:center_id>/', views.send_email, name='send_email'),

]
