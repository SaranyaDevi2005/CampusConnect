"""
URL configuration for placement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# placement/urls.py
from django.contrib import admin
from django.urls import path,include
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),  # Redirects to login
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),  # Optional: Implement logout
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('placement_coordinator_dashboard/', views.placement_coordinator_dashboard, name='placement_coordinator_dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),

    # Functionalities
    path('add_company/', views.add_company_view, name='add_company'),
    path('add_placement_details/', views.add_placement_details_view, name='add_placement_details'),
    path('add_placement_coordinator/', views.add_placement_coordinator_view, name='add_placement_coordinator'),
    path('add_students/', views.add_students_view, name='add_students'),
    path('view_details/', views.view_details_view, name='view_details'),
    path('submit-student-form/', views.submit_student_form_view, name='submit_student_form_view'),
    path('submit-feedback/', views.submit_feedback_view, name='submit_feedback'),
]
