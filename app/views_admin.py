from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

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
    patrimonios = Patrimonio.objects.all().order_by('id')
    paginator = Paginator(patrimonios, 4)
    pagina = request.GET.get('page', 1)
    lista = paginator.get_page(pagina)

    return render(
        request,
        "app_inventario/patrimonio_list.html",
        {"pagina": "patrimonio", "lista_patrimonios": lista}
    )


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

            patrimonios = Patrimonio.objects.filter(inventariante=inventariante)

            tabela = render_to_string(
                "app_inventario/partials/tabela_patrimonios.html",
                {"patrimonios": patrimonios},
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
    """ Exclui patrimônio e atualiza tabela HTMX """
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