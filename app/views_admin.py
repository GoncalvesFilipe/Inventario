from openpyxl import load_workbook, Workbook
from django.conf import settings
import os
import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import PatrimonioForm, InventarianteUserForm
from .models import Inventariante, Patrimonio
from .decorators import admin_required


# ==========================================================
# DASHBOARD ADMINISTRATIVO
# Função responsável por apresentar a página inicial do painel
# administrativo, acessível apenas mediante autenticação.
# ==========================================================
@login_required
def admin_dashboard(request):
    return render(request, "app_inventario/admin_dashboard.html")


# ==========================================================
# FECHAMENTO DE MODAL
# Retorna uma resposta vazia utilizada pelo HTMX para encerrar
# modais sem renderizar conteúdo adicional.
# ==========================================================
def close_modal(request):
    return HttpResponse("")


# ==========================================================
# LISTAGEM DE INVENTARIANTES
# Apresenta a lista completa de inventariantes cadastrados.
# A consulta não implementa filtragem e é destinada ao painel.
# ==========================================================
@login_required
def inventariantes_list(request):
    inventariantes = Inventariante.objects.all()
    return render(
        request,
        "app_inventario/partials/inventariantes_list.html",
        {"inventariantes": inventariantes}
    )


# ==========================================================
# LISTA PARCIAL (PARA HTMX)
# Renderiza apenas o fragmento da lista, empregado em recargas
# assíncronas sem reprocessamento da página completa.
# ==========================================================
@login_required
def inventariante_list_partial(request):
    inventariantes = Inventariante.objects.all()
    return render(
        request,
        "app_inventario/partials/inventariante_list.html",
        {"inventariantes": inventariantes}
    )

# ==========================================================
# ADIÇÃO DE INVENTARIANTE
# Implementa o fluxo completo para criação de usuário vinculado
# a um inventariante. O acesso é restrito a administradores.
# Utiliza HTMX para atualização dinâmica da interface.
# ==========================================================
@admin_required
def inventariante_add(request):
    if request.method == "POST":
        form = InventarianteUserForm(request.POST)

        if form.is_valid():
            form.save()

            # Renderiza um HTML de sucesso dentro do modal
            html = render_to_string(
                "app_inventario/partials/inventariante_success.html",
                {"mensagem": "Usuário inventariante salvo com sucesso!"},
                request=request
            )
            return HttpResponse(html)

        # Reapresenta o formulário com erros no contexto do modal
        html = render_to_string(
            "app_inventario/partials/inventariante_form.html",
            {"form": form},
            request=request
        )
        return HttpResponse(html)

    # Solicitação inicial (GET) → formulário limpo
    form = InventarianteUserForm()
    return render(
        request,
        "app_inventario/partials/inventariante_form.html",
        {"form": form}
    )


# ==========================================================
# EDIÇÃO DE INVENTARIANTE
# ----------------------------------------------------------
# Responsável por atualizar os dados vinculados a um inventariante.
# ==========================================================
@admin_required
def inventariante_edit(request, pk):
    inventariante = get_object_or_404(Inventariante, pk=pk)
    user = inventariante.user

    if request.method == "POST":
        form = InventarianteUserForm(request.POST, instance=inventariante, user=user)

        if form.is_valid():
            form.save()

            # Renderiza mensagem de sucesso dentro do modal
            html = render_to_string(
                "app_inventario/partials/inventariante_edit_success.html",
                {"mensagem": "Usuário inventariante atualizado com sucesso!"},
                request=request
            )

            response = HttpResponse(html)
            # Dispara trigger para atualizar a lista
            response["HX-Trigger"] = json.dumps({
                "reload": True
            })
            return response

        # Se houver erros, reapresenta o formulário
        html = render_to_string(
            "app_inventario/partials/inventariante_form.html",
            {
                "form": form,
                "inventariante": inventariante,
                "is_edit": True   # <<< ESSENCIAL para diferenciar edição
            },
            request=request
        )
        return HttpResponse(html)

    # GET inicial → formulário preenchido
    form = InventarianteUserForm(instance=inventariante, user=user)
    return render(
        request,
        "app_inventario/partials/inventariante_form.html",
        {
            "form": form,
            "inventariante": inventariante,
            "is_edit": True   # <<< ESSENCIAL para diferenciar edição
        }
    )


# ==========================================================
# CONFIRMAÇÃO DE EXCLUSÃO DE INVENTARIANTE
# Exibe modal solicitando confirmação prévia antes de proceder
# à remoção definitiva do registro.
# ==========================================================
@admin_required
def inventariante_delete_confirm(request, pk):
    inventariante = get_object_or_404(Inventariante, pk=pk)
    return render(
        request,
        "app_inventario/partials/inventariante_delete_confirm.html",
        {"inventariante": inventariante}
    )


# ==========================================================
# EXCLUSÃO DEFINITIVA DE INVENTARIANTE
# Realiza a remoção tanto do registro Inventariante quanto do
# usuário associado, caso exista, e aciona recarga dinâmica da
# listagem via HTMX.
# ==========================================================
@admin_required
def inventariante_delete(request, pk):
    inventariante = get_object_or_404(Inventariante, pk=pk)

    if request.method == "POST":
        try:
            if inventariante.user:
                inventariante.user.delete()
        except Exception:
            pass

        inventariante.delete()

        inventariantes = Inventariante.objects.all()
        html = render_to_string(
            "app_inventario/partials/inventariantes_list.html",
            {"inventariantes": inventariantes},
            request=request
        )

        response = HttpResponse(html)
        response["HX-Trigger"] = json.dumps({
            "closeModal": True,
            "reloadInventariantes": True
        })
        return response

    return HttpResponse(status=405)



# ==========================================================
# PATRIMÔNIOS
# Módulo responsável pelo gerenciamento completo dos bens
# patrimoniais, incluindo listagem, cadastro, edição e exclusão.
# ==========================================================


# ==========================================================
# LISTA DE PATRIMÔNIOS
# Implementa busca, paginação e segregação dos resultados com
# base no perfil do usuário (administrador ou inventariante).
# ==========================================================
@login_required
def patrimonio_list(request):
    search_query = request.GET.get('q')
    pagina_numero = request.GET.get('page', 1)

    # ======================================================
    # Regra unificada de privilégio administrativo
    # Considera usuários Superusuário ou pertencentes
    # ao grupo "Presidente" como administradores do sistema.
    # ======================================================
    is_admin = (
        request.user.is_superuser or
        request.user.groups.filter(name="Presidente").exists()
    )

    # Usuário administrador → acesso irrestrito
    if is_admin:
        patrimonios = Patrimonio.objects.all()
    else:
        # Usuário padrão → limitado aos seus próprios patrimônios
        inventariante = get_object_or_404(Inventariante, user=request.user)
        patrimonios = Patrimonio.objects.filter(inventariante=inventariante)

    # Mecanismo de busca textual
    if search_query:
        patrimonios = patrimonios.filter(
            Q(patrimonio__icontains=search_query) |
            Q(descricao__icontains=search_query) |
            Q(setor__icontains=search_query) |
            Q(dependencia__icontains=search_query)
        )

    patrimonios = patrimonios.order_by('id')

    # Paginação configurada com 4 itens por página
    paginator = Paginator(patrimonios, 4)

    try:
        lista_patrimonios = paginator.page(pagina_numero)
    except PageNotAnInteger:
        lista_patrimonios = paginator.page(1)
    except EmptyPage:
        lista_patrimonios = paginator.page(paginator.num_pages)

    context = {
        "pagina": "patrimonio",
        "lista_patrimonios": lista_patrimonios,
        "search_query": search_query or "",
        # Flag simples para controle de interface no template
        "is_admin": is_admin,
    }
    
    return render(request, "app_inventario/patrimonio_list.html", context)

# ==========================================================
# FORMULÁRIO HTMX DE PATRIMÔNIO
# Cria novas entradas patrimoniais e retorna apenas a tabela
# atualizada, evitando recarga completa da página.
# ==========================================================
@login_required
def patrimonio_form(request):
    inventariante = get_object_or_404(Inventariante, user=request.user)

    if request.method == "POST":
        form = PatrimonioForm(request.POST)

        if form.is_valid():
            patrimonio = form.save(commit=False)
            patrimonio.inventariante = inventariante
            patrimonio.save()

            patrimonios = Patrimonio.objects.filter(inventariante=inventariante)

            tabela = render_to_string(
                "app_inventario/partials/tabela_patrimonios.html",
                {"patrimonios": patrimonios},
                request=request
            )
            return HttpResponse(tabela)

    form = PatrimonioForm()
    return render(
        request,
        "app_inventario/partials/form_patrimonio.html",
        {"form": form}
    )


# ==========================================================
# ADIÇÃO DE PATRIMÔNIO
# Tratamento específico para inserção convencional de dados
# patrimoniais, preservando associação obrigatória ao usuário.
# ==========================================================
@login_required
def patrimonio_add(request):
    inventariante = get_object_or_404(Inventariante, user=request.user)

    if request.method == "POST":
        form = PatrimonioForm(request.POST, user=request.user)
        if form.is_valid():
            patrimonio = form.save(commit=False)
            patrimonio.inventariante = inventariante
            patrimonio.save()
            return HttpResponse("OK")
    else:
        form = PatrimonioForm(user=request.user)

    return render(
        request,
        "app_inventario/partials/form_patrimonio.html",
        {"form": form}
    )


# ==========================================================
# EDIÇÃO DE PATRIMÔNIO
# Permite atualização de dados já cadastrados. Suporta uploads
# e recarrega a página ao concluir alterações.
# ==========================================================
@login_required
def patrimonio_edit(request, pk):
    patrimonio = get_object_or_404(Patrimonio, pk=pk)

    if request.method == "POST":
        form = PatrimonioForm(request.POST, request.FILES, instance=patrimonio)
        if form.is_valid():
            form.save()
            return HttpResponse("", headers={"HX-Refresh": "true"})
    else:
        form = PatrimonioForm(instance=patrimonio)

    return render(
        request,
        "app_inventario/partials/form_patrimonio.html",
        {"form": form, "modo_edicao": True, "patrimonio": patrimonio}
    )


# ==========================================================
# CONFIRMAÇÃO DE EXCLUSÃO DE PATRIMÔNIO
# Exibe modal prévio, garantindo segurança na operação de
# remoção de bens associados ao inventariante.
# ==========================================================
@login_required
def confirmar_exclusao_patrimonio(request, pk):
    inventariante = get_object_or_404(Inventariante, user=request.user)
    patrimonio = get_object_or_404(Patrimonio, pk=pk, inventariante=inventariante)

    return render(
        request,
        "app_inventario/partials/confirmar_exclusao_patrimonio.html",
        {"patrimonio": patrimonio}
    )


# ==========================================================
# EXCLUSÃO DEFINITIVA DE PATRIMÔNIO
# Realiza a remoção de bens vinculados ao inventariante logado.
# Opera tanto com POST quanto com DELETE, permitindo integração
# com HTMX e outros clientes assíncronos.
# ==========================================================
@login_required
@csrf_exempt
def excluir_patrimonio(request, pk):
    inventariante = get_object_or_404(Inventariante, user=request.user)

    if request.method in ["POST", "DELETE"]:
        patrimonio = get_object_or_404(Patrimonio, pk=pk, inventariante=inventariante)
        patrimonio.delete()

        patrimonios = Patrimonio.objects.filter(inventariante=inventariante)

        return render(
            request,
            "app_inventario/partials/tabela_patrimonios.html",
            {"patrimonios": patrimonios}
        )

    return HttpResponse(status=405)


# ==========================================================
# REGISTRO EM PLANILHA
# ----------------------------------------------------------
# View responsável por inserir dados em uma planilha Excel,
# associando explicitamente o registro ao usuário autenticado.
# Esta funcionalidade é restrita ao painel administrativo.
# ==========================================================
@login_required
def adicionar_na_planilha(request):
    """
    Registra uma nova linha em planilha Excel, criando o arquivo
    automaticamente caso ainda não exista no diretório media.
    """

  
    usuario = request.user

    # Caminho absoluto do arquivo Excel
    caminho_planilha = os.path.join(
        settings.BASE_DIR,
        "registros.xlsx"
    )
    
    # Verifica se a planilha já existe
    if os.path.exists(caminho_planilha):
        # Abre planilha existente
        workbook = load_workbook(caminho_planilha)
        sheet = workbook.active
    else:
        # Cria nova planilha
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Registros"

        # Cabeçalho inicial
        sheet.append([
            "ID Usuário",
            "Username",
            "Nome Completo",
            "Descrição",
            "Valor"
        ])

    # Montagem da nova linha
    nova_linha = [
        usuario.id,
        usuario.username,
        usuario.get_full_name(),
        "Descrição do registro",
        150.00
    ]

    # Inserção e salvamento
    sheet.append(nova_linha)
    workbook.save(caminho_planilha)

    return HttpResponse("Registro salvo com sucesso")

# ==========================================================
# FUNÇÃO DE AUTORIZAÇÃO
# ----------------------------------------------------------
# Responsável por centralizar a regra de
# autorização aplicada às rotinas administrativas sensíveis
# do sistema.
#
# O acesso é concedido exclusivamente a:
# - Superusuário
# - Usuário/Presidente"
# Ambos são considerados perfis de nível administrativo pleno,
# possuindo autorização irrestrita para:
# - Inclusão de registros
# - Gerenciamento de listas
# - Operações sensíveis do sistema
# ==========================================================
def presidente_ou_superuser(user):
    """
    Critério de autorização:
    - Superusuário do sistema (is_superuser)
    OU
    - Usuário pertencente ao grupo 'Presidente'
    """
    return (
        user.is_authenticated and (
            user.is_superuser or
            user.groups.filter(name="Presidente").exists()
        )
    )


# ==========================================================
# REGISTRO DE PLANILHA (UPLOAD MANUAL)
# ----------------------------------------------------------
# Responsável por permitir o envio manual da planilha

# Funcionalidade restrita a usuários com perfil:
# Presidente ou Superusuário.
# ==========================================================
@login_required
@user_passes_test(presidente_ou_superuser)
def upload_planilha(request):
    """
    Recebe e armazena a planilha Excel enviada manualmente.
    O arquivo será salvo com nome padronizado no diretório
    de mídia do projeto, substituindo a versão anterior
    quando existente.
    """

    if request.method == "POST" and request.FILES.get("planilha"):
        planilha = request.FILES["planilha"]

        # Garante a existência do diretório de mídia
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        # Armazena a planilha com nome padronizado
        storage = FileSystemStorage(location=settings.MEDIA_ROOT)
        storage.save("registros.xlsx", planilha)

        # Retorno simples, mantendo o padrão das demais views
        return HttpResponse("Planilha enviada com sucesso", status=200)

    # Requisição GET → exibição do formulário de upload
    return render(request, "app_inventario/upload_planilha.html")