from django.urls import path
from . import views_admin

urlpatterns = [
    path('admin-dashboard/', views_admin.admin_dashboard, name='admin_dashboard'),

    # Rotas HTMX
    path('usuarios/', views_admin.usuarios_list, name='usuarios_list'),
    path('patrimonios/', views_admin.patrimonios_list, name='patrimonios_list'),
    path('usuario/<int:pk>/editar/', views_admin.usuario_edit, name='usuario_edit'),
]
