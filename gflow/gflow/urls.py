from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>G-Flow - Gestion de projets étudiants</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f0f4f8; }
                h1 { color: #4F46E5; }
                .btn { background: #4F46E5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px; }
            </style>
        </head>
        <body>
            <h1>📚 G-Flow</h1>
            <h2>Gestion de projets étudiants</h2>
            <p>Plateforme collaborative pour étudiants et enseignants</p>
            <div>
                <a href="/admin/" class="btn">Administration</a>
                <a href="/accounts/login/" class="btn">Connexion</a>
            </div>
            <p style="margin-top: 30px; color: #666;">Comptes test: admin / Admin1234!</p>
        </body>
        </html>
    """)

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
]