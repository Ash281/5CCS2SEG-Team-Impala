"""
URL configuration for task_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from tasks import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('new_password/<uuid:token>/', views.ChangePassword.as_view(), name='new_password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),

    path('create_team/', views.CreateTeamView.as_view(), name='create_team'),
    # path('team/<int:id>/dashboard/', views.TeamDashboardView.as_view(), name='team_dashboard'),
    path('team/<int:id>/', views.TeamDashboardView.as_view(), name='team_dashboard'),
    path('remove_members/<int:id>/', views.RemoveMembersView.as_view(), name='remove_members'),
    path('team/<int:team_id>/add_members/', views.AddMembersView.as_view(), name='add_members'),
    path('email_verify/', views.EmailVerification.as_view(), name='email_verify'),
    path('join_team/<uuid:token>/', views.JoinTeamView.as_view(), name='join_team'),
    path('leave_team/<int:id>/', views.LeaveTeamView.as_view(), name='leave_team'),
    path('team/<int:id>/delete/', views.DeleteTeamView.as_view(), name='delete_team'),

    path('create_task/<int:id>/', views.CreateTaskView.as_view(), name='create_task'),
    # path('task_list/', views.task_list, name='task_list'),

    path('tasks/<str:task_title>/', views.task_detail, name='task_detail'),
    path('tasks/edit/<str:task_title>/', views.edit_task, name='edit_task'),
    path('tasks/complete/<str:task_title>/', views.mark_task_complete, name='mark_task_complete'),
    path('tasks/delete/<str:task_title>/', views.delete_task, name='delete_task'),

    path('my_teams/', views.my_teams, name='my_teams'),
    path('my_tasks/', views.my_tasks, name='my_tasks'),

]
