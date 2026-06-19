from django.contrib import messages as flash
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import User, Project, Application, Message, Notification, Evaluation, ActivityLog
from .forms import SignUpForm, ProfileForm, ProjectForm, ApplicationForm, MessageForm, EvaluationForm
from .utils import projects_to_csv, project_to_pdf, search_scholar, notify


def _is_admin(u): return u.is_authenticated and (u.is_superuser or getattr(u, 'role', '') == 'admin')
def _is_teacher(u): return u.is_authenticated and getattr(u, 'role', '') == 'teacher'
def _is_student(u): return u.is_authenticated and getattr(u, 'role', '') == 'student'


def home(request):
    stats = {
        'projects': Project.objects.count(),
        'students': User.objects.filter(role='student').count(),
        'teachers': User.objects.filter(role='teacher').count(),
        'open_projects': Project.objects.filter(status='open').count(),
    }
    featured = Project.objects.filter(status='open')[:6]
    return render(request, 'core/home.html', {'stats': stats, 'featured': featured})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            flash.success(request, "Bienvenue sur G-Flow !")
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def dashboard(request):
    u = request.user
    ctx = {}
    if _is_admin(u):
        return redirect('admin_dashboard')
    if _is_teacher(u):
        my_projects = Project.objects.filter(teacher=u)
        pending_apps = Application.objects.filter(project__teacher=u, status='pending')
        ctx.update({
            'my_projects': my_projects,
            'project_count': my_projects.count(),
            'pending_apps': pending_apps[:5],
            'pending_count': pending_apps.count(),
            'students_count': User.objects.filter(projects_assigned__teacher=u).distinct().count(),
        })
        return render(request, 'core/dashboard_teacher.html', ctx)
    # student
    my_apps = Application.objects.filter(student=u).select_related('project')
    ctx.update({
        'open_projects': Project.objects.filter(status='open')[:6],
        'my_applications': my_apps[:5],
        'my_projects': u.projects_assigned.all(),
        'pending_count': my_apps.filter(status='pending').count(),
        'accepted_count': my_apps.filter(status='accepted').count(),
    })
    return render(request, 'core/dashboard_student.html', ctx)


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            flash.success(request, "Profil mis à jour.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'core/profile.html', {'form': form})


@login_required
def toggle_theme(request):
    new = 'dark' if request.user.theme_preference == 'light' else 'light'
    request.user.theme_preference = new
    request.user.save(update_fields=['theme_preference'])
    resp = HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('dashboard')))
    resp.set_cookie('gflow_theme', new, max_age=60*60*24*365)
    return resp


def project_list(request):
    qs = Project.objects.select_related('teacher').all()
    q = request.GET.get('q','').strip()
    domain = request.GET.get('domain','').strip()
    status = request.GET.get('status','').strip()
    difficulty = request.GET.get('difficulty','').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(technologies__icontains=q))
    if domain: qs = qs.filter(domain__iexact=domain)
    if status: qs = qs.filter(status=status)
    if difficulty: qs = qs.filter(difficulty=difficulty)
    paginator = Paginator(qs, 9)
    page = paginator.get_page(request.GET.get('page'))
    domains = Project.objects.values_list('domain', flat=True).distinct()
    return render(request, 'core/project_list.html', {
        'page_obj': page, 'q': q, 'domain': domain, 'status': status, 'difficulty': difficulty, 'domains': domains
    })


def project_detail(request, pk):
    project = get_object_or_404(Project.objects.select_related('teacher').prefetch_related('students','applications'), pk=pk)
    user_app = None
    if request.user.is_authenticated and _is_student(request.user):
        user_app = project.applications.filter(student=request.user).first()
    return render(request, 'core/project_detail.html', {'project': project, 'user_app': user_app})


@login_required
@user_passes_test(_is_teacher)
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            p.teacher = request.user
            p.save()
            flash.success(request, "Projet créé avec succès.")
            return redirect('project_detail', p.pk)
    else:
        form = ProjectForm()
    return render(request, 'core/project_form.html', {'form': form, 'title': 'Nouveau projet'})


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not (_is_admin(request.user) or project.teacher == request.user):
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            flash.success(request, "Projet mis à jour.")
            return redirect('project_detail', project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'core/project_form.html', {'form': form, 'title': 'Modifier le projet', 'project': project})


@login_required
@require_POST
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not (_is_admin(request.user) or project.teacher == request.user):
        return HttpResponseForbidden()
    project.delete()
    flash.success(request, "Projet supprimé.")
    return redirect('project_list')


@login_required
@user_passes_test(_is_student)
def project_apply(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.status != 'open':
        flash.error(request, "Ce projet n'accepte plus de candidatures.")
        return redirect('project_detail', pk)
    if Application.objects.filter(project=project, student=request.user).exists():
        flash.warning(request, "Vous avez déjà candidaté.")
        return redirect('project_detail', pk)
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            app = form.save(commit=False)
            app.project = project
            app.student = request.user
            app.save()
            notify(project.teacher, "Nouvelle candidature",
                   f"{request.user.get_full_name() or request.user.username} a candidaté à « {project.title} ».",
                   reverse('applications_inbox'))
            try:
                send_mail("G-Flow — Nouvelle candidature",
                          f"{request.user} a candidaté à votre projet '{project.title}'.",
                          'noreply@gflow.cm', [project.teacher.email or 'noreply@gflow.cm'], fail_silently=True)
            except Exception: pass
            flash.success(request, "Candidature envoyée.")
            return redirect('project_detail', pk)
    else:
        form = ApplicationForm()
    return render(request, 'core/application_form.html', {'form': form, 'project': project})


@login_required
def project_pdf(request, pk):
    project = get_object_or_404(Project, pk=pk)
    pdf = project_to_pdf(project)
    resp = HttpResponse(pdf, content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename="projet-{project.pk}.pdf"'
    return resp


@login_required
def projects_export_csv(request):
    if _is_teacher(request.user):
        qs = Project.objects.filter(teacher=request.user)
    elif _is_admin(request.user):
        qs = Project.objects.all()
    else:
        qs = request.user.projects_assigned.all()
    csv_data = projects_to_csv(qs)
    resp = HttpResponse(csv_data, content_type='text/csv')
    resp['Content-Disposition'] = 'attachment; filename="projets-gflow.csv"'
    return resp


@login_required
@user_passes_test(_is_teacher)
def applications_inbox(request):
    apps = Application.objects.filter(project__teacher=request.user).select_related('project','student').order_by('-created_at')
    status = request.GET.get('status','')
    if status: apps = apps.filter(status=status)
    return render(request, 'core/applications_inbox.html', {'apps': apps, 'status': status})


@login_required
@user_passes_test(_is_teacher)
def application_decide(request, pk, action):
    app = get_object_or_404(Application, pk=pk, project__teacher=request.user)
    if action == 'accept':
        if app.project.slots_left <= 0:
            flash.error(request, "Plus de place disponible.")
            return redirect('applications_inbox')
        app.status = 'accepted'
        app.save()
        app.project.students.add(app.student)
        if app.project.students.count() >= app.project.max_students:
            app.project.status = 'in_progress'
            app.project.save()
        notify(app.student, "Candidature acceptée 🎉",
               f"Votre candidature à « {app.project.title} » a été acceptée.",
               reverse('project_detail', args=[app.project.pk]))
    elif action == 'reject':
        app.status = 'rejected'; app.save()
        notify(app.student, "Candidature refusée",
               f"Votre candidature à « {app.project.title} » a été refusée.",
               reverse('project_detail', args=[app.project.pk]))
    flash.success(request, "Décision enregistrée.")
    return redirect('applications_inbox')


@login_required
@user_passes_test(_is_student)
def my_applications(request):
    apps = Application.objects.filter(student=request.user).select_related('project').order_by('-created_at')
    return render(request, 'core/my_applications.html', {'apps': apps})


@login_required
def messages_inbox(request):
    msgs = request.user.received_messages.select_related('sender').all()
    return render(request, 'core/messages_inbox.html', {'msgs': msgs, 'box': 'inbox'})


@login_required
def messages_sent(request):
    msgs = request.user.sent_messages.select_related('recipient').all()
    return render(request, 'core/messages_inbox.html', {'msgs': msgs, 'box': 'sent'})


@login_required
def message_new(request):
    initial = {}
    rid = request.GET.get('to')
    if rid:
        try: initial['recipient'] = User.objects.get(pk=rid)
        except User.DoesNotExist: pass
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            m = form.save(commit=False)
            m.sender = request.user
            m.save()
            notify(m.recipient, "Nouveau message",
                   f"De {request.user.get_full_name() or request.user.username}: {m.subject}",
                   reverse('message_detail', args=[m.pk]))
            flash.success(request, "Message envoyé.")
            return redirect('messages_sent')
    else:
        form = MessageForm(initial=initial)
    return render(request, 'core/message_form.html', {'form': form})


@login_required
def message_detail(request, pk):
    m = get_object_or_404(Message, pk=pk)
    if request.user not in (m.sender, m.recipient) and not _is_admin(request.user):
        return HttpResponseForbidden()
    if m.recipient == request.user and not m.is_read:
        m.is_read = True; m.save(update_fields=['is_read'])
    return render(request, 'core/message_detail.html', {'m': m})


@login_required
def notifications_list(request):
    notifs = request.user.notifications.all()
    return render(request, 'core/notifications.html', {'notifs': notifs})


@login_required
@require_POST
def notifications_mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('notifications_list')


@login_required
@user_passes_test(_is_teacher)
def evaluate(request, project_id, student_id):
    project = get_object_or_404(Project, pk=project_id, teacher=request.user)
    student = get_object_or_404(User, pk=student_id, role='student')
    if student not in project.students.all():
        return HttpResponseForbidden()
    instance = Evaluation.objects.filter(project=project, student=student).first()
    if request.method == 'POST':
        form = EvaluationForm(request.POST, instance=instance)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.project = project; ev.student = student; ev.teacher = request.user
            ev.save()
            notify(student, "Nouvelle évaluation",
                   f"Vous avez reçu la note {ev.grade}/20 pour « {project.title} ».",
                   reverse('project_detail', args=[project.pk]))
            flash.success(request, "Évaluation enregistrée.")
            return redirect('project_detail', project.pk)
    else:
        form = EvaluationForm(instance=instance)
    return render(request, 'core/evaluate.html', {'form': form, 'project': project, 'student': student})


@login_required
def research(request):
    q = request.GET.get('q','').strip()
    results = search_scholar(q) if q else []
    return render(request, 'core/research.html', {'q': q, 'results': results})


# ====== ADMIN ======
@login_required
@user_passes_test(_is_admin)
def admin_dashboard(request):
    ctx = {
        'user_count': User.objects.count(),
        'student_count': User.objects.filter(role='student').count(),
        'teacher_count': User.objects.filter(role='teacher').count(),
        'project_count': Project.objects.count(),
        'open_count': Project.objects.filter(status='open').count(),
        'in_progress_count': Project.objects.filter(status='in_progress').count(),
        'completed_count': Project.objects.filter(status='completed').count(),
        'application_count': Application.objects.count(),
        'pending_app_count': Application.objects.filter(status='pending').count(),
        'recent_users': User.objects.order_by('-date_joined')[:5],
        'recent_projects': Project.objects.order_by('-created_at')[:5],
        'recent_logs': ActivityLog.objects.select_related('user').order_by('-created_at')[:8],
        'avg_grade': Evaluation.objects.aggregate(a=Avg('grade'))['a'] or 0,
    }
    return render(request, 'core/admin_dashboard.html', ctx)


@login_required
@user_passes_test(_is_admin)
def admin_users(request):
    qs = User.objects.all().order_by('-date_joined')
    q = request.GET.get('q','').strip()
    role = request.GET.get('role','').strip()
    if q: qs = qs.filter(Q(username__icontains=q)|Q(email__icontains=q)|Q(first_name__icontains=q)|Q(last_name__icontains=q))
    if role: qs = qs.filter(role=role)
    paginator = Paginator(qs, 15)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'core/admin_users.html', {'page_obj': page, 'q': q, 'role': role})


@login_required
@user_passes_test(_is_admin)
@require_POST
def admin_user_toggle(request, pk):
    u = get_object_or_404(User, pk=pk)
    if u == request.user:
        flash.error(request, "Vous ne pouvez pas vous désactiver vous-même.")
    else:
        u.is_active = not u.is_active; u.save(update_fields=['is_active'])
        flash.success(request, f"Utilisateur {'activé' if u.is_active else 'désactivé'}.")
    return redirect('admin_users')


@login_required
@user_passes_test(_is_admin)
@require_POST
def admin_user_delete(request, pk):
    u = get_object_or_404(User, pk=pk)
    if u == request.user:
        flash.error(request, "Vous ne pouvez pas vous supprimer vous-même.")
    else:
        u.delete(); flash.success(request, "Utilisateur supprimé.")
    return redirect('admin_users')


@login_required
@user_passes_test(_is_admin)
def admin_projects(request):
    qs = Project.objects.select_related('teacher').all()
    q = request.GET.get('q','').strip()
    if q: qs = qs.filter(Q(title__icontains=q)|Q(domain__icontains=q))
    paginator = Paginator(qs, 15)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'core/admin_projects.html', {'page_obj': page, 'q': q})


@login_required
@user_passes_test(_is_admin)
def admin_logs(request):
    qs = ActivityLog.objects.select_related('user').all()
    q = request.GET.get('q','').strip()
    if q: qs = qs.filter(Q(action__icontains=q)|Q(path__icontains=q)|Q(user__username__icontains=q))
    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'core/admin_logs.html', {'page_obj': page, 'q': q})


@login_required
@user_passes_test(_is_admin)
def admin_stats_json(request):
    by_status = list(Project.objects.values('status').annotate(c=Count('id')))
    by_role = list(User.objects.values('role').annotate(c=Count('id')))
    by_difficulty = list(Project.objects.values('difficulty').annotate(c=Count('id')))
    return JsonResponse({'by_status': by_status, 'by_role': by_role, 'by_difficulty': by_difficulty})
