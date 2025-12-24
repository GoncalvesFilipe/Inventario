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

from .decorators import presidente_ou_superuser


# ==========================================================
# DASHBOARD ADMINISTRATIVO
# Função responsável por apresentar a página inicial do painel
# administrativo, acessível apenas mediante autenticação.
# ==========================================================
@login_required
def admin_dashboard(request):
    return render(request, "app_inventario/admin_dashboard.html")


# ==========================================================
# FUNÇÃO DE AUTORIZAÇÃO
# ----------------------------------------------------------
# Responsável por centralizar a regra de autorização aplicada
# às rotinas administrativas sensíveis do sistema.
#
# O acesso é concedido exclusivamente a:
# - Superusuário
# - Inventariante com flag 'presidente=True'
# ==========================================================
def presidente_ou_superuser(user):
    return (
        user.is_authenticated and (
            user.is_superuser or
            (hasattr(user, "inventariante") and user.inventariante.presidente)
        )
    )


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
# ----------------------------------------------------------
# Implementa busca, paginação e segregação dos resultados com
# base no perfil do usuário (administrador ou inventariante).
# ==========================================================
@login_required
def patrimonio_list(request):
    search_query = request.GET.get('q')
    pagina_numero = request.GET.get('page', 1)

    # Flag administrativa (superuser ou inventariante presidente)
    is_admin = (
        request.user.is_superuser or
        (hasattr(request.user, "inventariante") and request.user.inventariante.presidente)
    )

    # Administrador → acesso irrestrito
    if is_admin:
        patrimonios = Patrimonio.objects.all()
    else:
        inventariante = get_object_or_404(Inventariante, user=request.user)
        patrimonios = Patrimonio.objects.filter(inventariante=inventariante)

    # Filtro de busca textual
    if search_query:
        patrimonios = patrimonios.filter(
            Q(patrimonio__icontains=search_query) |
            Q(descricao__icontains=search_query) |
            Q(setor__icontains=search_query) |
            Q(dependencia__icontains=search_query)
        )

    # Paginação
    paginator = Paginator(patrimonios.order_by('id'), 6)
    try:
        lista_patrimonios = paginator.page(pagina_numero)
    except (PageNotAnInteger, EmptyPage):
        lista_patrimonios = paginator.page(1)

    return render(request, "app_inventario/patrimonio_list.html", {
        "pagina": "patrimonio",
        "lista_patrimonios": lista_patrimonios,
        "search_query": search_query or "",
        "is_admin": is_admin,
        "user": request.user,  # importante para usar no template
    })


# ==========================================================
# FORMULÁRIO HTMX DE PATRIMÔNIO
# ----------------------------------------------------------
# Permite inventariantes comuns adicionarem seus próprios bens.
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
            tabela = render_to_string(
                "app_inventario/partials/tabela_patrimonios.html",
                {"patrimonios": Patrimonio.objects.filter(inventariante=inventariante)},
                request=request
            )
            return HttpResponse(tabela)
    return render(request, "app_inventario/partials/form_patrimonio.html", {"form": PatrimonioForm()})


# ==========================================================
# ADIÇÃO DE PATRIMÔNIO
# ----------------------------------------------------------
# Restrito a superusuário ou inventariante presidente.
# ==========================================================
@login_required
@user_passes_test(presidente_ou_superuser)
def patrimonio_add(request):
    inventariante = get_object_or_404(Inventariante, user=request.user)
    if request.method == "POST":
        form = PatrimonioForm(request.POST, user=request.user)
        if form.is_valid():
            patrimonio = form.save(commit=False)
            patrimonio.inventariante = inventariante
            patrimonio.save()
            return HttpResponse("OK")
    return render(request, "app_inventario/partials/form_patrimonio.html", {"form": PatrimonioForm(user=request.user)})

# ==========================================================
# EDIÇÃO DE PATRIMÔNIO
# ----------------------------------------------------------
# Restrito a superusuário ou inventariante presidente.
# ==========================================================
@login_required
@user_passes_test(presidente_ou_superuser)
def patrimonio_edit(request, pk):
    patrimonio = get_object_or_404(Patrimonio, pk=pk)
    if request.method == "POST":
        form = PatrimonioForm(request.POST, request.FILES, instance=patrimonio)
        if form.is_valid():
            form.save()
            return HttpResponse("", headers={"HX-Refresh": "true"})
    return render(request, "app_inventario/partials/form_patrimonio.html", {
        "form": PatrimonioForm(instance=patrimonio),
        "modo_edicao": True,
        "patrimonio": patrimonio
    })

# ==========================================================
# CONFIRMAÇÃO DE EXCLUSÃO DE PATRIMÔNIO
# ----------------------------------------------------------
# Restrito a superusuário ou inventariante presidente.
# ==========================================================
@login_required
@user_passes_test(presidente_ou_superuser)
def confirmar_exclusao_patrimonio(request, pk):
    patrimonio = get_object_or_404(Patrimonio, pk=pk)
    return render(request, "app_inventario/partials/confirmar_exclusao_patrimonio.html", {"patrimonio": patrimonio})


# ==========================================================
# EXCLUSÃO DE PATRIMÔNIO
# ----------------------------------------------------------
# Restrito a superusuário ou inventariante presidente.
# ==========================================================
@login_required
@user_passes_test(presidente_ou_superuser)
def excluir_patrimonio(request, pk):
    if request.method != "POST":
        return HttpResponse(status=405)
    patrimonio = get_object_or_404(Patrimonio, pk=pk)
    patrimonio.delete()
    response = HttpResponse("")
    response["HX-Trigger"] = json.dumps({"patrimonioExcluido": True})
    return response


# ==========================================================
# EXCLUSÃO DE PLANILHA DE PATRIMÔNIO
# ----------------------------------------------------------
# Responsável por remover o arquivo físico da planilha Excel
# e também excluir todos os registros de patrimônio do banco.
#
# Fluxo:
# 1) Recebe requisição POST via HTMX
# 2) Remove o arquivo "registros.xlsx" do diretório MEDIA_ROOT
# 3) Exclui todos os registros da tabela Patrimonio
# 4) Dispara evento HTMX "planilhaExcluida" para feedback
#    visual e recarregamento da página
# ==========================================================
@login_required
@user_passes_test(presidente_ou_superuser)
def excluir_planilha(request):
    # ------------------------------------------------------
    # Validação do método HTTP
    # ------------------------------------------------------
    if request.method != "POST":
        return HttpResponse(status=405)

    # ------------------------------------------------------
    # Caminho absoluto da planilha
    # ------------------------------------------------------
    caminho_planilha = os.path.join(settings.MEDIA_ROOT, "registros.xlsx")

    # ------------------------------------------------------
    # Remoção do arquivo físico, se existir
    # ------------------------------------------------------
    if os.path.exists(caminho_planilha):
        os.remove(caminho_planilha)

    # ------------------------------------------------------
    # Exclusão de todos os registros de patrimônio no banco
    # ------------------------------------------------------
    Patrimonio.objects.all().delete()

    # ------------------------------------------------------
    # Retorno da resposta + disparo de evento HTMX
    # ------------------------------------------------------
    response = HttpResponse("")
    response["HX-Trigger"] = json.dumps({
        "planilhaExcluida": True
    })
    return response


# ==========================================================
# CONFIRMAÇÃO DE EXCLUSÃO DE PLANILHA
# ----------------------------------------------------------
# Exibe modal solicitando confirmação prévia antes de proceder
# à remoção definitiva da planilha e dos registros vinculados.
# ==========================================================
@login_required
@user_passes_test(presidente_ou_superuser)
def excluir_planilha_confirm(request):
    return render(
        request,
        "app_inventario/partials/excluir_planilha_confirm.html"
    )



# ==========================================================
# REGISTRO EM PLANILHA
# ----------------------------------------------------------
# View responsável por inserir dados em uma planilha Excel,
# associando explicitamente o registro ao inventariante
# autenticado e criando também o registro no banco de dados.
# Esta funcionalidade é restrita ao painel administrativo.
# ==========================================================
@login_required
def adicionar_na_planilha(request):
    """
    Registra uma nova linha em planilha Excel, criando o arquivo
    automaticamente caso ainda não exista no diretório media.
    Além disso, insere o registro no banco de dados Patrimonio.
    """

    #  Recupera usuário e inventariante vinculado
    usuario = request.user
    inventariante = get_object_or_404(Inventariante, user=usuario)

    # Define caminho absoluto do arquivo Excel
    caminho_planilha = os.path.join(
        settings.MEDIA_ROOT,  # usar MEDIA_ROOT em vez de BASE_DIR
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

    # Inserção e salvamento na planilha
    sheet.append(nova_linha)
    workbook.save(caminho_planilha)

    # Inserção no banco de dados Patrimonio
    # Gera número de patrimônio automaticamente:
    # pega o último ID e soma 1
    ultimo = Patrimonio.objects.order_by("-id").first()
    if ultimo:
        patrimonio_numero = ultimo.patrimonio + 1
    else:
        patrimonio_numero = 1

    descricao = "Descrição do registro"
    setor = "Setor padrão"
    dependencia = "Dependência padrão"
    situacao = "localizado"

    Patrimonio.objects.create(
        patrimonio=patrimonio_numero,
        descricao=descricao,
        setor=setor,
        dependencia=dependencia,
        situacao=situacao,
        inventariante=inventariante
    )

    # Retorno da resposta
    return HttpResponse("Registro salvo com sucesso")



# ==========================================================
# REGISTRO DE PLANILHA (UPLOAD MANUAL)
# ----------------------------------------------------------
# View responsável exclusivamente pelo processamento 
# da planilha oficial de registros do sistema.
#
# Funcionalidade restrita a usuários com perfil:
# - Presidente
# - Superusuário
#
# Após o processamento:
# - Os dados são persistidos no banco de dados
# - Nenhum conteúdo HTML é retornado
# - Um evento HTMX é disparado para controle do fluxo
#   no frontend (feedback visual, fechamento do modal
#   e atualização da listagem)
# ==========================================================
@login_required
@user_passes_test(presidente_ou_superuser)
def upload_planilha(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    if not request.FILES.get("planilha"):
        return HttpResponse(status=400)

    planilha = request.FILES["planilha"]

    # Garante diretório de mídia
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

    caminho_planilha = os.path.join(settings.MEDIA_ROOT, "registros.xlsx")

    # Salva arquivo enviado
    fs = FileSystemStorage(location=settings.MEDIA_ROOT)
    fs.save("registros.xlsx", planilha)

    # Abre planilha com openpyxl
    workbook = load_workbook(caminho_planilha)
    sheet = workbook.active

    # Recupera inventariante vinculado ao usuário logado
    inventariante = get_object_or_404(Inventariante, user=request.user)

    # Itera linhas a partir da segunda (ignora cabeçalho)
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if not any(row):  # ignora linhas totalmente vazias
            continue

        patrimonio_numero, descricao, setor, dependencia, situacao, *rest = row

        # Valida número do patrimônio
        try:
            patrimonio_numero = int(patrimonio_numero)
        except (TypeError, ValueError):
            continue

        # Cria registro no banco vinculado ao inventariante
        Patrimonio.objects.create(
            patrimonio=patrimonio_numero,
            descricao=descricao or "",
            setor=setor or "",
            dependencia=dependencia or "",
            situacao=situacao or "localizado",
            inventariante=inventariante
        )

    # Dispara evento HTMX para frontend
    response = HttpResponse("")
    response["HX-Trigger"] = "planilhaAtualizada"
    return response


# ==========================================================
# ATUALIZAÇÃO RÁPIDA DE SITUAÇÃO
# Permite alterar a 'situação' de um patrimônio diretamente
# na tabela via select (HTMX).
# ==========================================================
@login_required
def patrimonio_update_situacao(request, pk):
    # Obtém o patrimônio. É importante garantir que o usuário
    # logado tenha permissão para alterar (regra básica: só o próprio inventariante ou admin)
    
    # Tentamos obter o patrimônio, considerando que ele existe
    patrimonio = get_object_or_404(Patrimonio, pk=pk)

    if request.method == 'POST':
        # O HTMX envia o valor do select no corpo da requisição POST
        nova_situacao = request.POST.get('situacao')
        
        if nova_situacao:
            patrimonio.situacao = nova_situacao
            patrimonio.save()
            
            # Após salvar, renderizamos o SELECT novamente,
            # forçando o HTMX a recarregar apenas o elemento modificado.
            return render(
                request,
                "app_inventario/partials/situacao_select.html", 
                {"p": patrimonio}
            )
        
    # Se a requisição não for POST, apenas retorna o select atual
    return render(
        request,
        "app_inventario/partials/situacao_select.html", 
        {"p": patrimonio}
    )

@login_required
@user_passes_test(presidente_ou_superuser)
def upload_planilha_modal(request):
    """
    Retorna o template que contém o formulário do modal.
    """
    return render(request, "app_inventario/upload_planilha.html")

