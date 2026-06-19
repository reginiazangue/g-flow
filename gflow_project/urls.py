from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.contrib.auth.views import LoginView, LogoutView
from gflow_project.views import register
def home(request):
    return HttpResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>G-Flow - Gestion de projets étudiants</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }
                .container {
                    text-align: center;
                    padding: 50px;
                    color: white;
                }
                h1 { font-size: 48px; margin-bottom: 20px; }
                .subtitle { font-size: 20px; margin-bottom: 30px; opacity: 0.9; }
                .btn {
                    display: inline-block;
                    padding: 12px 30px;
                    margin: 10px;
                    background: white;
                    color: #667eea;
                    text-decoration: none;
                    border-radius: 25px;
                    font-weight: bold;
                }
                .btn:hover { transform: scale(1.05); }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📚 G-Flow</h1>
                <div class="subtitle">Plateforme de gestion de projets étudiants</div>
                <div>
                    <a href="/admin/" class="btn">🔐 Administration</a>
                    <a href="/accounts/login/" class="btn">👤 Connexion</a>
                    <a href="/register/" class="btn">📝 Inscription</a>
                </div>
                <p style="margin-top: 40px;">Compte test: admin / Admin1234!</p>
            </div>
        </body>
        </html>
    """)

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', register, name='register'),
]