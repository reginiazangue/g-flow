import pytest
from django.urls import reverse
from core.models import User, Project, Application

@pytest.fixture
def teacher(db):
    return User.objects.create_user(username='t1', password='pwd12345!', role='teacher')

@pytest.fixture
def student(db):
    return User.objects.create_user(username='s1', password='pwd12345!', role='student')

@pytest.fixture
def project(db, teacher):
    return Project.objects.create(title='P1', description='d', domain='Web', technologies='Django', teacher=teacher)

def test_home(client, db):
    r = client.get('/'); assert r.status_code == 200

def test_login_page(client):
    r = client.get('/login/'); assert r.status_code == 200

def test_signup_page(client):
    r = client.get('/signup/'); assert r.status_code == 200

def test_project_list(client, db):
    r = client.get('/projects/'); assert r.status_code == 200

def test_project_detail(client, project):
    r = client.get(f'/projects/{project.pk}/'); assert r.status_code == 200

def test_dashboard_requires_login(client):
    r = client.get('/dashboard/'); assert r.status_code == 302

def test_student_dashboard(client, student):
    client.force_login(student)
    r = client.get('/dashboard/'); assert r.status_code == 200

def test_teacher_dashboard(client, teacher):
    client.force_login(teacher)
    r = client.get('/dashboard/'); assert r.status_code == 200

def test_apply_to_project(client, student, project):
    client.force_login(student)
    r = client.post(f'/projects/{project.pk}/apply/', {'motivation':'oui'})
    assert Application.objects.filter(student=student, project=project).exists()

def test_admin_dashboard_forbidden(client, student):
    client.force_login(student)
    r = client.get('/admin-panel/'); assert r.status_code in (302, 403)

def test_csv_export(client, teacher):
    client.force_login(teacher)
    r = client.get('/projects/export/csv/'); assert r.status_code == 200
    assert 'text/csv' in r['Content-Type']

def test_pdf_export(client, teacher, project):
    client.force_login(teacher)
    r = client.get(f'/projects/{project.pk}/pdf/'); assert r.status_code == 200
    assert r['Content-Type'] == 'application/pdf'
