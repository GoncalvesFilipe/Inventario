from django.contrib import admin
from django.urls import path, include
from app import views as app_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', app_views.index, name='index'),

    # Rotas de autenticação
    path('users/', include('users.urls')),  # ✅ inclui todas as rotas de login/logout/register

    # Painel administrativo
    path('painel/', include('app.urls_admin')),
]
