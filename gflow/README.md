# G-Flow — Gestion de projets étudiants

Plateforme Django moderne pour gérer les projets étudiants : étudiants, enseignants, administrateurs.

## ✨ Fonctionnalités

### Niveau 1 — Obligatoire
- Authentification (inscription/connexion/déconnexion) avec rôles (Étudiant, Enseignant, Admin)
- CRUD projets (titre, description, technologies, difficulté, statut, deadline)
- Candidatures étudiants → enseignants (accepter/refuser)
- Profils utilisateurs (avatar, CV, bio)

### Niveau 2 — Intermédiaire
- Dashboards par rôle (étudiant, enseignant, admin)
- Recherche & filtres avancés (domaine, statut, difficulté, technologies)
- Pagination
- Notifications (email console + in-app)
- Mode clair/sombre persistant (cookie + DB)

### Niveau 3 / Bonus
- ✅ Upload CV (FileField)
- ✅ Export CSV des projets
- ✅ Export PDF d'une fiche projet (ReportLab)
- ✅ Messagerie interne (sender → recipient)
- ✅ Évaluations (note /20 par l'enseignant)
- ✅ Dashboard admin avec graphiques (Chart.js)
- ✅ Cache Django (LocMem)
- ✅ Tests unitaires (pytest, 12 tests)
- ✅ Dockerfile + docker-compose + CI GitHub Actions
- ✅ Recherche scientifique (Crossref API)
- ✅ Logs d'activité (middleware)
- ✅ Loaders professionnels (barre top + spinner overlay)

## 🚀 Installation

```bash
# 1. Créer environnement virtuel
python -m venv venv
source venv/bin/activate   # Windows : venv\Scripts\activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configuration
cp .env.example .env

# 4. Base de données
python manage.py makemigrations
python manage.py migrate

# 5. Données de démo
python manage.py seed_data

# 6. Lancer
python manage.py runserver
```

Ouvrez http://127.0.0.1:8000

## 👤 Comptes de démo

| Rôle        | Identifiant   | Mot de passe   |
|-------------|---------------|----------------|
| Admin       | `admin`       | `Admin1234!`   |
| Enseignant  | `prof.kamga`  | `Teacher1234!` |
| Étudiant    | `etudiant1`   | `Student1234!` |

## 🧪 Tests

```bash
pytest -v
```

## 🐳 Docker

```bash
docker-compose up --build
```

## 📦 Librairies utilisées

- **Django 4.2** — framework web
- **djangorestframework** — API REST (extensible)
- **django-crispy-forms + crispy-bootstrap5** — formulaires élégants
- **Pillow** — images
- **reportlab** — génération PDF
- **python-dotenv** — variables d'environnement
- **requests** — appels API externes (Crossref)
- **django-filter** — filtres avancés
- **whitenoise** — fichiers statiques en prod
- **pytest + pytest-django** — tests
- **gunicorn** — serveur WSGI prod

## 🎨 Design

- Police : **Plus Jakarta Sans** (titres) + **Inter** (texte)
- Palette : Indigo (#4F46E5) → Cyan (#06B6D4)
- Mode sombre/clair via toggle (icône lune/soleil dans la navbar)
- Loader professionnel : barre top fluide + overlay spinner sur formulaires
- Responsive mobile-first (Bootstrap 5)

## 📁 Architecture

```
gflow/
├── core/
│   ├── models.py            # User, Project, Application, Message, Evaluation, Notification, ActivityLog
│   ├── views.py             # 30+ vues
│   ├── forms.py             # Formulaires
│   ├── admin.py             # Configuration Django Admin
│   ├── middleware.py        # Logs d'activité
│   ├── context_processors.py
│   ├── utils.py             # CSV, PDF, Crossref
│   ├── urls.py
│   ├── management/commands/seed_data.py
│   ├── templates/core/      # 26 templates
│   ├── templates/registration/
│   └── static/core/         # CSS, JS
├── gflow/                   # settings, urls, wsgi
├── tests/
├── manage.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

Conçu avec ❤️ pour les étudiants — © 2026 G-Flow

## 🌍 Multilingue (FR / EN)

G-Flow supporte le **Français** et l'**Anglais** sur toutes les interfaces.

- Sélecteur de langue dans la navbar (icône 🌐 traduction)
- Choix persistant via cookie `django_language` (LocaleMiddleware)
- Tous les templates utilisent `{% trans %}` / `{% load i18n %}`
- Fichiers de traduction dans `locale/fr/LC_MESSAGES/` et `locale/en/LC_MESSAGES/`

### Mettre à jour les traductions
```bash
# Extraire les chaînes des templates
python manage.py makemessages -l en -l fr --ignore=venv
# Éditer locale/<lang>/LC_MESSAGES/django.po puis :
python manage.py compilemessages
```
