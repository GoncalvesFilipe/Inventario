from django.urls import path
from . import views_admin

urlpatterns = [
    path('admin-dashboard/', views_admin.admin_dashboard, name='admin_dashboard'),

    # Rotas HTMX
    path('usuarios/', views_admin.usuarios_list, name='usuarios_list'),
    path('patrimonios/', views_admin.patrimonios_list, name='patrimonios_list'),
    
    # Patrimônio
    path('patrimonio/form/', views_admin.patrimonio_form, name='patrimonio_form'),
    path('patrimonio/add/', views_admin.patrimonio_add, name='patrimonio_add'),
    path('patrimonio/<int:pk>/editar/', views_admin.patrimonio_edit, name='editar_patrimonio'),

    # Usuários
    path('usuario/adicionar/', views_admin.usuario_add, name='usuario_add'),
    path('usuario/<int:pk>/editar/', views_admin.usuario_edit, name='usuario_edit'),
    path('usuario/<int:pk>/excluir/', views_admin.usuario_delete, name='usuario_delete'),
]
