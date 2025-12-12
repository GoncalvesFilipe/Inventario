import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import PatrimonioForm, InventarianteUserForm
from .models import Inventariante, Patrimonio
from .decorators import admin_required
from django_htmx.http import trigger_client_event


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

            # Retorna resposta sem corpo para evitar inserções indevidas no modal.
            response = HttpResponse(status=204)
            response["HX-Trigger"] = json.dumps({
                "reloadInventariantes": True,  # Solicita recarga da listagem
                "closeModal": True             # Solicita encerramento do modal
            })
            return response

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
    """
    Edita os dados de um inventariante específico.
    - request: objeto da requisição HTTP.
    - pk: chave primária do inventariante.
    """

    # Recupera o inventariante ou retorna erro 404 se não encontrado.
    inventariante = get_object_or_404(Inventariante, pk=pk)
    user = inventariante.user

    if request.method == "POST":
        # Instancia o formulário com os dados submetidos.
        form = InventarianteUserForm(request.POST, instance=inventariante, user=user)

        if form.is_valid():
            form.save()  # Persiste alterações no banco.

            if request.htmx:
                # Retorna resposta vazia e dispara evento HTMX
                # para fechar modal e atualizar a interface.
                response = HttpResponse("")
                trigger_client_event(response, "inventarianteAtualizado")
                return response

            # Fluxo tradicional: redireciona para a lista.
            return redirect("inventariantes_list")

        # Caso inválido, retorna novamente o formulário com erros.
        return render(
            request,
            "app_inventario/partials/inventariante_edit_form.html",
            {"form": form, "inventariante": inventariante}
        )

    # Fluxo GET: renderiza o formulário de edição.
    form = InventarianteUserForm(instance=inventariante, user=user)
    return render(
        request,
        "app_inventario/partials/inventariante_edit_form.html",
        {"form": form, "inventariante": inventariante}
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

    # Usuário administrador → acesso irrestrito
    if request.user.is_superuser:
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
