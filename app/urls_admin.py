from django.urls import path
from . import views_admin

urlpatterns = [
    # Dashboard
    path('admin-dashboard/', views_admin.admin_dashboard, name='admin_dashboard'),

    # Listagens HTMX
    path('inventariantes/', views_admin.inventariantes_list, name='inventariantes_list'),
    path('patrimonios/', views_admin.patrimonio_list, name='patrimonio_list'),

    # Patrimônio
    path('patrimonio/form/', views_admin.patrimonio_form, name='patrimonio_form'),
    path('patrimonio/add/', views_admin.patrimonio_add, name='patrimonio_add'),
    path('patrimonio/<int:pk>/editar/', views_admin.patrimonio_edit, name='patrimonio_edit'),
    path('patrimonio/<int:pk>/confirmar-exclusao/', views_admin.confirmar_exclusao_patrimonio, name='confirmar_exclusao_patrimonio'),
    path('patrimonio/<int:pk>/excluir/', views_admin.excluir_patrimonio, name='excluir_patrimonio'),

    # Inventariante
    path('inventariante/adicionar/', views_admin.inventariante_add, name='inventariante_add'),
    path('inventariante/<int:pk>/editar/', views_admin.inventariante_edit, name='inventariante_edit'),
    path('inventariante/<int:pk>/excluir/', views_admin.inventariante_delete, name='inventariante_delete'),
]
