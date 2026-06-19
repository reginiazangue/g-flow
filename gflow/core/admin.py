from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Project, Application, Message, Notification, Evaluation, ActivityLog


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username','email','first_name','last_name','role','is_active','date_joined')
    list_filter = ('role','is_active','is_staff')
    search_fields = ('username','email','first_name','last_name')
    fieldsets = UserAdmin.fieldsets + (
        ('Profil G-Flow', {'fields': ('role','avatar','bio','phone','department','cv','theme_preference')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Profil G-Flow', {'fields': ('email','first_name','last_name','role')}),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title','teacher','domain','difficulty','status','max_students','created_at')
    list_filter = ('status','difficulty','domain')
    search_fields = ('title','description','domain','technologies')
    filter_horizontal = ('students',)
    autocomplete_fields = ('teacher',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student','project','status','created_at')
    list_filter = ('status',)
    search_fields = ('student__username','project__title')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender','recipient','subject','is_read','created_at')
    list_filter = ('is_read',)
    search_fields = ('subject','body')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user','title','is_read','created_at')
    list_filter = ('is_read',)


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('project','student','teacher','grade','created_at')
    search_fields = ('project__title','student__username')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user','action','ip','created_at')
    list_filter = ('method',)
    search_fields = ('user__username','path','action')
    readonly_fields = ('user','action','path','method','ip','user_agent','created_at')
