from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('theme/toggle/', views.toggle_theme, name='toggle_theme'),

    path('projects/', views.project_list, name='project_list'),
    path('projects/new/', views.project_create, name='project_create'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('projects/<int:pk>/apply/', views.project_apply, name='project_apply'),
    path('projects/<int:pk>/pdf/', views.project_pdf, name='project_pdf'),
    path('projects/export/csv/', views.projects_export_csv, name='projects_export_csv'),

    path('applications/', views.applications_inbox, name='applications_inbox'),
    path('applications/<int:pk>/<str:action>/', views.application_decide, name='application_decide'),
    path('my-applications/', views.my_applications, name='my_applications'),

    path('messages/', views.messages_inbox, name='messages_inbox'),
    path('messages/sent/', views.messages_sent, name='messages_sent'),
    path('messages/new/', views.message_new, name='message_new'),
    path('messages/<int:pk>/', views.message_detail, name='message_detail'),

    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/read-all/', views.notifications_mark_all_read, name='notifications_mark_all_read'),

    path('evaluate/<int:project_id>/<int:student_id>/', views.evaluate, name='evaluate'),

    path('research/', views.research, name='research'),

    # Admin custom dashboard
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/users/<int:pk>/toggle/', views.admin_user_toggle, name='admin_user_toggle'),
    path('admin-panel/users/<int:pk>/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('admin-panel/projects/', views.admin_projects, name='admin_projects'),
    path('admin-panel/logs/', views.admin_logs, name='admin_logs'),
    path('admin-panel/stats.json', views.admin_stats_json, name='admin_stats_json'),
]
