from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils import timezone


class User(AbstractUser):
    ROLE_STUDENT = 'student'
    ROLE_TEACHER = 'teacher'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_STUDENT, 'Étudiant'),
        (ROLE_TEACHER, 'Enseignant'),
        (ROLE_ADMIN, 'Administrateur'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    cv = models.FileField(upload_to='cvs/', blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    department = models.CharField(max_length=100, blank=True)
    theme_preference = models.CharField(max_length=10, default='light', choices=[('light','Clair'),('dark','Sombre')])

    @property
    def is_student(self): return self.role == self.ROLE_STUDENT
    @property
    def is_teacher(self): return self.role == self.ROLE_TEACHER
    @property
    def is_admin_role(self): return self.role == self.ROLE_ADMIN or self.is_superuser

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


class Project(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_OPEN = 'open'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Brouillon'),
        (STATUS_OPEN, 'Ouvert'),
        (STATUS_IN_PROGRESS, 'En cours'),
        (STATUS_COMPLETED, 'Terminé'),
    ]
    DIFFICULTY_CHOICES = [('easy','Facile'),('medium','Moyen'),('hard','Difficile')]

    title = models.CharField(max_length=200)
    description = models.TextField()
    domain = models.CharField(max_length=100)
    technologies = models.CharField(max_length=300, help_text="Séparées par des virgules")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    max_students = models.PositiveIntegerField(default=1)
    deadline = models.DateField(null=True, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects_supervised', limit_choices_to={'role': 'teacher'})
    students = models.ManyToManyField(User, related_name='projects_assigned', blank=True, limit_choices_to={'role': 'student'})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project_detail', args=[self.pk])

    @property
    def tech_list(self):
        return [t.strip() for t in self.technologies.split(',') if t.strip()]

    @property
    def slots_left(self):
        return max(self.max_students - self.students.count(), 0)


class Application(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'En attente'),
        (STATUS_ACCEPTED, 'Acceptée'),
        (STATUS_REJECTED, 'Refusée'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications', limit_choices_to={'role': 'student'})
    motivation = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('project', 'student')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student} -> {self.project} ({self.get_status_display()})"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender} -> {self.recipient}: {self.subject}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    url = models.CharField(max_length=300, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class Evaluation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='evaluations')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluations_received')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluations_given')
    grade = models.DecimalField(max_digits=4, decimal_places=2, help_text="Note sur 20")
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'student')
        ordering = ['-created_at']


class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    path = models.CharField(max_length=300, blank=True)
    method = models.CharField(max_length=10, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
