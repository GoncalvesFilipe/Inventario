from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import PatrimonioForm, InventarianteForm
from .models import Inventariante, Patrimonio
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# DASHBOARD PRINCIPAL
@login_required
def admin_dashboard(request):
    return render(request, "app_inventario/admin_dashboard.html")


# LISTAGEM DE INVENTARIANTES
@login_required
def inventariantes_list(request):
    inventariantes = Inventariante.objects.all()
    return render(
        request,
        "app_inventario/partials/inventariantes_list.html",
        {"inventariantes": inventariantes}
    )


# ADICIONAR INVENTARIANTE (HTMX)
@login_required
def inventariante_add(request):
    if request.method == "POST":
        form = InventarianteForm(request.POST)

        if form.is_valid():
            inventariante = form.save(commit=False)
            inventariante.user = request.user
            inventariante.save()

            inventariantes = Inventariante.objects.all()
            html = render_to_string(
                "app_inventario/partials/usuarios_list.html",
                {"usuarios": inventariantes},
                request=request
            )
            return HttpResponse(html)

        # Form inválido
        html = render_to_string(
            "app_inventario/partials/form_inventariante.html",
            {"form": form},
            request=request
        )
        return HttpResponse(html)

    form = InventarianteForm()
    return render(
        request,
        "app_inventario/partials/form_inventariante.html",
        {"form": form}
    )


# EDITAR INVENTARIANTE
@login_required
def inventariante_edit(request, pk):
    inventariante = get_object_or_404(Inventariante, pk=pk)

    if request.method == "POST":
        form = InventarianteForm(request.POST, instance=inventariante)
        if form.is_valid():
            form.save()
            return redirect('inventariantes_list')

    else:
        form = InventarianteForm(instance=inventariante)

    return render(
        request,
        "app_inventario/partials/form_inventariante.html",
        {"form": form}
    )


# DELETAR INVENTARIANTE
@login_required
def inventariante_delete(request, pk):
    inventariante = get_object_or_404(Inventariante, pk=pk)
    inventariante.delete()
    return redirect('inventariantes_list')


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


# EDITAR PATRIMÔNIO
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
