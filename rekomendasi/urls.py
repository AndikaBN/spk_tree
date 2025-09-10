
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('', views.dashboard, name='dashboard'),

    path('students/', views.students_list, name='students_list'),
    path('students/add/', views.student_create, name='student_create'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),

    path('train/', views.train_model, name='train_model'),
    path('calculation/<int:student_id>/', views.calculation_details, name='predict_for_student'),
    path('results/', views.results, name='results'),
]
