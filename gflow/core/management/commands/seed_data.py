from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import User, Project, Application, Notification, Message


class Command(BaseCommand):
    help = "Seed G-Flow with demo data"

    def handle(self, *args, **kwargs):
        self.stdout.write("→ Seeding G-Flow…")

        # Admin
        admin, _ = User.objects.get_or_create(username='admin', defaults={'email':'admin@gflow.cm','first_name':'Super','last_name':'Admin','role':'admin','is_staff':True,'is_superuser':True})
        admin.set_password('Admin1234!'); admin.is_staff=True; admin.is_superuser=True; admin.role='admin'; admin.save()

        # Teachers
        teachers = []
        for i, (u, fn, ln, dept) in enumerate([
            ('prof.kamga','Paul','Kamga','Informatique'),
            ('prof.mballa','Sophie','Mballa','Génie logiciel'),
            ('prof.nkomo','André','Nkomo','Data Science'),
        ]):
            t, _ = User.objects.get_or_create(username=u, defaults={'email':f'{u}@gflow.cm','first_name':fn,'last_name':ln,'role':'teacher','department':dept})
            t.set_password('Teacher1234!'); t.role='teacher'; t.department=dept; t.save(); teachers.append(t)

        # Students
        students = []
        for i in range(1, 11):
            s, _ = User.objects.get_or_create(username=f'etudiant{i}', defaults={'email':f'etudiant{i}@gflow.cm','first_name':f'Étudiant{i}','last_name':'Demo','role':'student'})
            s.set_password('Student1234!'); s.role='student'; s.save(); students.append(s)

        # Projects
        proj_data = [
            ('Plateforme e-learning IA','Développer une plateforme adaptive avec IA pour personnaliser l\'apprentissage.','Intelligence Artificielle','Python, Django, TensorFlow, React','hard','open',2),
            ('Application mobile de covoiturage','App mobile pour étudiants du campus.','Mobile','Flutter, Firebase, Google Maps API','medium','open',3),
            ('Système de gestion bibliothèque','Modernisation du SI bibliothèque universitaire.','Système d\'information','Django, PostgreSQL, Bootstrap','easy','open',2),
            ('Chatbot d\'orientation académique','Chatbot intelligent pour conseiller les étudiants.','NLP','Python, Rasa, FastAPI','medium','in_progress',1),
            ('Dashboard analytique campus','Visualisation des données campus en temps réel.','Data Science','Django, Chart.js, Pandas','medium','open',2),
            ('IoT — Monitoring salles de classe','Capteurs connectés pour optimiser l\'occupation.','IoT','Arduino, MQTT, Node.js','hard','open',3),
            ('Site vitrine du laboratoire','Site institutionnel pour le labo recherche.','Web','HTML, CSS, JavaScript','easy','completed',1),
            ('Détection de fraude examens','ML pour détecter anomalies durant examens en ligne.','Machine Learning','Python, scikit-learn, OpenCV','hard','open',2),
        ]
        projects = []
        for i, (title, desc, dom, tech, diff, st, n) in enumerate(proj_data):
            p, _ = Project.objects.get_or_create(title=title, defaults={
                'description': desc, 'domain': dom, 'technologies': tech, 'difficulty': diff,
                'status': st, 'max_students': n, 'teacher': teachers[i % len(teachers)],
                'deadline': timezone.now().date() + timedelta(days=30 + i*7),
            })
            projects.append(p)

        # Applications
        for s in students[:6]:
            for p in projects[:3]:
                Application.objects.get_or_create(student=s, project=p, defaults={'motivation': f'Je suis très intéressé par {p.title}. J\'ai les compétences requises.'})

        # Sample messages
        if teachers and students:
            Message.objects.get_or_create(sender=teachers[0], recipient=students[0], subject='Bienvenue !', defaults={'body':'Bonjour, bienvenue sur G-Flow.'})

        # Notifications
        for s in students[:3]:
            Notification.objects.get_or_create(user=s, title='Bienvenue sur G-Flow', defaults={'body':'Explorez les projets disponibles.'})

        self.stdout.write(self.style.SUCCESS("✓ Seed terminé !"))
        self.stdout.write("  Admin     → admin / Admin1234!")
        self.stdout.write("  Enseignant→ prof.kamga / Teacher1234!")
        self.stdout.write("  Étudiant  → etudiant1 / Student1234!")
