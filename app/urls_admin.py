from django.urls import path
from . import views_admin
from .views_admin import close_modal

# Definição das rotas da aplicação relacionadas à administração.
urlpatterns = [
    # Rota para o painel administrativo principal (dashboard).
    path('admin-dashboard/', views_admin.admin_dashboard, name='admin_dashboard'),
    
    # Rota para fechamento de modal (interação dinâmica).
    path("close-modal/", close_modal, name="close_modal"),

    # Rotas para listagens dinâmicas via HTMX.
    path('inventariantes/', views_admin.inventariantes_list, name='inventariantes_list'),
    path('patrimonios/', views_admin.patrimonio_list, name='patrimonio_list'),

    # Rotas relacionadas ao gerenciamento de patrimônio.
    path('patrimonio/form/', views_admin.patrimonio_form, name='patrimonio_form'),  # Exibição do formulário.
    path('patrimonio/add/', views_admin.patrimonio_add, name='patrimonio_add'),  # Inclusão de novo patrimônio.
    path('patrimonio/<int:pk>/editar/', views_admin.patrimonio_edit, name='patrimonio_edit'),  # Edição de patrimônio existente.
    path('patrimonio/<int:pk>/confirmar-exclusao/', views_admin.confirmar_exclusao_patrimonio, name='confirmar_exclusao_patrimonio'),  # Confirmação de exclusão.
    path('patrimonio/<int:pk>/excluir/', views_admin.excluir_patrimonio, name='excluir_patrimonio'),  # Exclusão definitiva.
    path('patrimonio/<int:pk>/update_situacao/', views_admin.patrimonio_update_situacao, name='patrimonio_update_situacao'),

    # Rotas relacionadas ao gerenciamento de inventariantes.
    path('inventariante/adicionar/', views_admin.inventariante_add, name='inventariante_add'),  # Inclusão de novo inventariante.
    path('inventariante/<int:pk>/editar/', views_admin.inventariante_edit, name='inventariante_edit'),  # Edição de inventariante existente.

    # (1) Rota para carregar modal de confirmação de exclusão (requisição GET).
    path('inventariante/<int:pk>/confirmar-exclusao/', views_admin.inventariante_delete_confirm, name='inventariante_delete_confirm'),

    # (2) Rota para executar a exclusão de inventariante (requisição POST).
    path('inventariante/<int:pk>/excluir/', views_admin.inventariante_delete, name='inventariante_delete'),
    
    # ROTA PARA ADICIONAR PLANILHA
    path("planilha/adicionar/", views_admin.adicionar_na_planilha,name="adicionar_na_planilha"),
    path("patrimonios/upload-planilha/", views_admin.upload_planilha,name="upload_planilha"),
    path("planilha/modal/", views_admin.upload_planilha_modal,name="upload_planilha_modal"),

]    
     