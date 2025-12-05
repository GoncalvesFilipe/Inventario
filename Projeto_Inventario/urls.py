from django.contrib import admin
from django.urls import path, include
from app import views as app_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', app_views.index, name='index'),

    # Rotas da aplicação de usuários
    path('users/', include('users.urls')),

    # Painel administrativo
    path('painel/', include('app.urls_admin')),
]
