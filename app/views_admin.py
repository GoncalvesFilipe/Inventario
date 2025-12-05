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


# ======= DASHBOARD =======
@login_required
def admin_dashboard(request):
    return render(request, "app_inventario/admin_dashboard.html")


# ======= MODAL RESTRIÇÃO =======
def close_modal(request):
    return HttpResponse("")


# ======= LISTA DE INVENTARIANTES =======
@login_required
def inventariantes_list(request):
    inventariantes = Inventariante.objects.all()
    return render(
        request,
        "app_inventario/partials/inventariantes_list.html",
        {"inventariantes": inventariantes}
    )


@login_required
def inventariante_list_partial(request):
    inventariantes = Inventariante.objects.all()
    return render(
        request,
        "app_inventario/partials/inventariante_list.html",
        {"inventariantes": inventariantes}
    )


# ======= ADICIONAR INVENTARIANTE =======
@admin_required
def inventariante_add(request):
    if request.method == "POST":
        form = InventarianteUserForm(request.POST)

        if form.is_valid():
            form.save()

            inventariantes = Inventariante.objects.all()
            html = render_to_string(
                "app_inventario/partials/inventariantes_list.html",
                {"inventariantes": inventariantes},
                request=request
            )
            return HttpResponse(html)

        # Form inválido
        html = render_to_string(
            "app_inventario/partials/inventariante_form.html",
            {"form": form},
            request=request
        )
        return HttpResponse(html)

    form = InventarianteUserForm()
    return render(
        request,
        "app_inventario/partials/inventariante_form.html",
        {"form": form}
    )


# ======= EDITAR INVENTARIANTE =======
@admin_required
def inventariante_edit(request, pk):
    inventariante = get_object_or_404(Inventariante, pk=pk)
    user = inventariante.user

    if request.method == "POST":
        form = InventarianteUserForm(request.POST, instance=user)

        if form.is_valid():
            form.save()

            if request.headers.get("HX-Request"):
                return HttpResponse("""
                <script>
                    const modalEl = document.getElementById('modalInventario');
                    if (modalEl) {
                        const modal = bootstrap.Modal.getInstance(modalEl) 
                                   || bootstrap.Modal.getOrCreateInstance(modalEl);
                        modal.hide();
                    }
                    htmx.trigger('#inventariante-list', 'reload');
                </script>
                """)

            return redirect("inventariantes_list")

        return render(
            request,
            "app_inventario/partials/inventariante_edit_form.html",
            {"form": form, "inventariante": inventariante}
        )

    # GET
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
        "app_inventario/partials/inventariante_edit_form.html",
        {"form": form, "inventariante": inventariante}
    )


# ======= CONFIRMAR EXCLUSÃO DE INVENTARIANTE =======
@admin_required
def inventariante_delete_confirm(request, pk):
    inventariante = get_object_or_404(Inventariante, pk=pk)
    return render(
        request,
        "app_inventario/partials/inventariante_delete_confirm.html",
        {"inventariante": inventariante}
    )


# ======= EXCLUIR INVENTARIANTE =======
@admin_required
def inventariante_delete(request, pk):
    inventariante = get_object_or_404(Inventariante, pk=pk)

    if request.method == "POST":
        inventariante.user.delete()
        inventariante.delete()

        inventariantes = Inventariante.objects.all()
        html = render_to_string(
            "app_inventario/partials/inventariantes_list.html",
            {"inventariantes": inventariantes},
            request=request
        )

        response = HttpResponse(html)
        response.headers["HX-Trigger"] = "closeModal reloadInventariantes"
        return response

    return HttpResponse(status=405)


# =======================================================
# ==================== PATRIMÔNIOS =======================
# =======================================================


# LISTA DE PATRIMÔNIOS
@login_required
def patrimonio_list(request):
    search_query = request.GET.get('q')
    pagina_numero = request.GET.get('page', 1)

    if request.user.is_superuser:
        patrimonios = Patrimonio.objects.all()
    else:
        inventariante = get_object_or_404(Inventariante, user=request.user)
        patrimonios = Patrimonio.objects.filter(inventariante=inventariante)

    if search_query:
        patrimonios = patrimonios.filter(
            Q(patrimonio__icontains=search_query) |
            Q(descricao__icontains=search_query) |
            Q(setor__icontains=search_query) |
            Q(dependencia__icontains=search_query)
        )

    patrimonios = patrimonios.order_by('id')

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


# FORM HTMX DE PATRIMÔNIO
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


# ADICIONAR PATRIMÔNIO
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


# EDITAR PATRIMÔNIO
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


# CONFIRMAR EXCLUSÃO DE PATRIMÔNIO
@login_required
def confirmar_exclusao_patrimonio(request, pk):
    inventariante = get_object_or_404(Inventariante, user=request.user)
    patrimonio = get_object_or_404(Patrimonio, pk=pk, inventariante=inventariante)

    return render(
        request,
        "app_inventario/partials/confirmar_exclusao_patrimonio.html",
        {"patrimonio": patrimonio}
    )


# EXCLUIR PATRIMÔNIO
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
