from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

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
                h1 {
                    font-size: 48px;
                    margin-bottom: 20px;
                }
                .subtitle {
                    font-size: 20px;
                    margin-bottom: 30px;
                    opacity: 0.9;
                }
                .btn {
                    display: inline-block;
                    padding: 12px 30px;
                    margin: 10px;
                    background: white;
                    color: #667eea;
                    text-decoration: none;
                    border-radius: 25px;
                    font-weight: bold;
                    transition: transform 0.3s;
                }
                .btn:hover {
                    transform: scale(1.05);
                }
                .features {
                    margin-top: 50px;
                    display: flex;
                    justify-content: center;
                    gap: 30px;
                    flex-wrap: wrap;
                }
                .feature {
                    background: rgba(255,255,255,0.2);
                    padding: 20px;
                    border-radius: 10px;
                    width: 200px;
                }
                .feature h3 {
                    margin: 0 0 10px 0;
                }
                .feature p {
                    font-size: 14px;
                    opacity: 0.9;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📚 G-Flow</h1>
                <div class="subtitle">Plateforme de gestion de projets étudiants</div>
                <div>
                    <a href="/admin/" class="btn">🔐 Administration</a>
                    <a href="/accounts/login/" class="btn">👤 Connexion</a>
                </div>
                <div class="features">
                    <div class="feature">
                        <h3>📁 Projets</h3>
                        <p>Créez et gérez vos projets</p>
                    </div>
                    <div class="feature">
                        <h3>👥 Équipes</h3>
                        <p>Collaborez en équipe</p>
                    </div>
                    <div class="feature">
                        <h3>📊 Évaluations</h3>
                        <p>Suivez les progrès</p>
                    </div>
                </div>
                <p style="margin-top: 40px; font-size: 12px; opacity: 0.7;">
                    Compte test: admin / Admin1234!
                </p>
            </div>
        </body>
        </html>
    """)

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
]