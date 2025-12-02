from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import models

from .forms import PatrimonioForm, InventarianteUserForm
from .models import Inventariante, Patrimonio
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# ======= DASHBOARD =======
@login_required
def admin_dashboard(request):
    """ Página inicial do painel administrativo """
    return render(request, "app_inventario/admin_dashboard.html")


# ======= INVENTARIANTES =======
@login_required
def inventariantes_list(request):
    """ Lista todos os inventariantes """
    inventariantes = Inventariante.objects.all()
    return render(
        request,
        "app_inventario/partials/inventariantes_list.html",
        {"inventariantes": inventariantes}
    )


@login_required
def inventariante_add(request):
    """
    Cria um inventariante.
    Usa InventarianteUserForm, que cria User + Inventariante.
    """
    if request.method == "POST":
        form = InventarianteUserForm(request.POST)

        if form.is_valid():
            form.save()

            # Recarrega lista após salvar
            inventariantes = Inventariante.objects.all()
            html = render_to_string(
                "app_inventario/partials/inventariantes_list.html",
                {"inventariantes": inventariantes},
                request=request
            )
            return HttpResponse(html)

        # Caso erro, recarrega o formulário com erros
        html = render_to_string(
            "app_inventario/partials/form_inventariante.html",
            {"form": form},
            request=request
        )
        return HttpResponse(html)

    # GET → mostra formulário vazio
    form = InventarianteUserForm()
    return render(request, "app_inventario/partials/form_inventariante.html", {"form": form})


@login_required
def inventariante_edit(request, pk):
    """
    Edita User + Inventariante no mesmo formulário unificado.
    """
    inventariante = get_object_or_404(Inventariante, pk=pk)
    user = inventariante.user

    if request.method == "POST":
        form = InventarianteUserForm(request.POST, instance=user)

        if form.is_valid():
            # Salva User
            user = form.save()

            # Atualiza Inventariante
            inventariante.matricula = form.cleaned_data["matricula"]
            inventariante.funcao = form.cleaned_data["funcao"]
            inventariante.telefone = form.cleaned_data["telefone"]
            inventariante.presidente = form.cleaned_data["presidente"]
            inventariante.ano_atuacao = form.cleaned_data["ano_atuacao"]
            inventariante.save()

            return redirect("inventariantes_list")

    else:
        # Preenche com valores do Inventariante
        form = InventarianteUserForm(
            instance=user,
            initial={
                "matricula": inventariante.matricula,
                "funcao": inventariante.funcao,
                "telefone": inventariante.telefone,
                "presidente": inventariante.presidente,
                "ano_atuacao": inventariante.ano_atuacao,
            }
        )

    return render(
        request,
        "app_inventario/partials/form_inventariante.html",
        {"form": form}
    )


@login_required
def inventariante_delete(request, pk):
    """ Deleta o inventariante e o usuário correspondente """
    inventariante = get_object_or_404(Inventariante, pk=pk)
    inventariante.user.delete()
    return redirect("inventariantes_list")


# ======= PATRIMÔNIO =======

# LISTA DE PATRIMÔNIOS
@login_required
def patrimonio_list(request):
    search = request.GET.get("search", "")

    lista = Patrimonio.objects.all()

    if search:
        lista = lista.filter(descricao__icontains=search)

    paginator = Paginator(lista, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    contexto = {
        "lista": page_obj,
        "search_query": f"&search={search}" if search else "",
    }

    if request.htmx:
        return render(request, "partials/tabela_patrimonios.html", contexto)

    return render(request, "patrimonio/patrimonio_list.html", contexto)



# FORMULÁRIO DE NOVO PATRIMÔNIO (USADO EM ALGUMAS PARTES)
@login_required
def patrimonio_form(request):
    """
    Form para cadastrar patrimônio via HTMX.
    O patrimônio é sempre vinculado ao inventariante logado.
    """
    inventariante = get_object_or_404(Inventariante, user=request.user)

    if request.method == "POST":
        form = PatrimonioForm(request.POST)

        if form.is_valid():
            patrimonio = form.save(commit=False)
            patrimonio.inventariante = inventariante
            patrimonio.save()

            # --- RECARREGAR LISTAGEM APÓS SALVAR ---
            busca = request.GET.get("busca", "")

            queryset = Patrimonio.objects.filter(inventariante=inventariante)

            if busca:
                queryset = queryset.filter(descricao__icontains=busca)

            paginator = Paginator(queryset.order_by("descricao"), 10)
            page_number = request.GET.get("page")
            lista_patrimonios = paginator.get_page(page_number)

            tabela = render_to_string(
                "app_inventario/partials/tabela_patrimonios.html",
                {
                    "lista_patrimonios": lista_patrimonios,
                    "busca": busca,
                },
                request=request
            )
            return HttpResponse(tabela)

    else:
        form = PatrimonioForm()

    return render(
        request,
        "app_inventario/partials/form_patrimonio.html",
        {"form": form}
    )


# ADICIONAR PATRIMÔNIO (HTMX)
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


@login_required
def patrimonio_edit(request, pk):
    patrimonio = get_object_or_404(Patrimonio, pk=pk)

    if request.method == "POST":
        form = PatrimonioForm(
            request.POST,
            request.FILES,
            instance=patrimonio
        )
        if form.is_valid():
            form.save()
            return HttpResponse("", headers={"HX-Refresh": "true"})
    else:
        form = PatrimonioForm(instance=patrimonio)

    return render(request, "app_inventario/partials/form_patrimonio.html", {
        "form": form,
        "modo_edicao": True,
        "patrimonio": patrimonio,
    })


@login_required
def confirmar_exclusao_patrimonio(request, pk):
    """ Renderiza modal de confirmação para excluir """
    inventariante = get_object_or_404(Inventariante, user=request.user)
    patrimonio = get_object_or_404(Patrimonio, pk=pk, inventariante=inventariante)

    return render(
        request,
        "app_inventario/partials/confirmar_exclusao_patrimonio.html",
        {"patrimonio": patrimonio}
    )


@login_required
@csrf_exempt
def excluir_patrimonio(request, pk):
    inventariante = get_object_or_404(Inventariante, user=request.user)

    if request.method in ["POST", "DELETE"]:
        patrimonio = get_object_or_404(Patrimonio, pk=pk, inventariante=inventariante)
        patrimonio.delete()

        busca = request.GET.get("busca", "")
        patrimonios = Patrimonio.objects.all().order_by("id")

        if busca:
            patrimonios = patrimonios.filter(
                models.Q(patrimonio__icontains=busca) |
                models.Q(descricao__icontains=busca) |
                models.Q(setor__icontains=busca) |
                models.Q(inventariante__user__first_name__icontains=busca) |
                models.Q(inventariante__user__last_name__icontains=busca)
            )

        paginator = Paginator(patrimonios, 6)
        page_number = request.GET.get("page", 1)
        lista = paginator.get_page(page_number)

        return render(
            request,
            "app_inventario/partials/tabela_patrimonios.html",
            {
                "lista_patrimonios": lista,
                "busca": busca,
            }
        )

    return HttpResponse(status=405)

