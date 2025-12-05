from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import PatrimonioForm, InventarianteUserForm
from .models import Inventariante, Patrimonio
from .decorators import admin_required


# ======= DASHBOARD =======
@login_required
def admin_dashboard(request):
    """ Página inicial do painel administrativo """
    return render(request, "app_inventario/admin_dashboard.html")

# ======= MODAL RESTRIÇÃO =======
def close_modal(request):
    return HttpResponse("")


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
def inventariante_list_partial(request):
    inventariantes = Inventariante.objects.all()
    return render(request, "app_inventario/partials/inventariante_list.html", {"inventariantes": inventariantes})


@admin_required
def inventariante_add(request):
    """
    Cadastro via painel admin (HTMX):
    - Cria User
    - Cria Inventariante
    - NÃO faz login
    - Atualiza a lista via HTMX
    """
    if request.method == "POST":
        form = InventarianteUserForm(request.POST)

        if form.is_valid():
            form.save()

            # Lista atualizada
            inventariantes = Inventariante.objects.all()
            html = render_to_string(
                "app_inventario/partials/inventariantes_list.html",
                {"inventariantes": inventariantes},
                request=request
            )

            return HttpResponse(html)

        # Em caso de erro → retorna o próprio formulário preenchido
        html = render_to_string(
            "app_inventario/partials/inventariante_form.html",
            {"form": form},
            request=request
        )
        return HttpResponse(html)

    # GET → formulário vazio
    form = InventarianteUserForm()
    return render(
        request,
        "app_inventario/partials/inventariante_form.html",
        {"form": form}
    )


@admin_required
def inventariante_edit(request, pk):
    inventariante = get_object_or_404(Inventariante, pk=pk)
    user = inventariante.user

    if request.method == "POST":
        form = InventarianteUserForm(request.POST, instance=user)

        if form.is_valid():
            form.save()  # já salva User + Inventariante

            if request.headers.get("HX-Request"):
                return HttpResponse("""
                <script>
                    const modalEl = document.getElementById('modalInventario');
                    if (modalEl) {
                        const modal = bootstrap.Modal.getInstance(modalEl) || bootstrap.Modal.getOrCreateInstance(modalEl);
                        modal.hide();
                    }
                    htmx.trigger('#inventariante-list', 'reload');
                </script>
                """)


            return redirect("inventariante_list")

        # Form inválido → re-renderiza modal via HTMX
        return render(
            request,
            "app_inventario/partials/inventariante_edit_form.html",
            {"form": form, "inventariante": inventariante}
        )

    else:
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
    
@admin_required
def inventariante_delete_confirm(request, pk):
    inventariante = get_object_or_404(Inventariante, pk=pk)
    return render(request, 'app_inventario/partials/inventariante_delete_confirm.html', {
        'inventariante': inventariante
    })

@admin_required
def inventariante_delete(request, pk):
    inventariante = get_object_or_404(Inventariante, pk=pk)

    if request.method == "POST":
        # Exclui o usuário vinculado
        inventariante.user.delete()
        inventariante.delete()

        # Atualiza a lista de inventariantes
        inventariantes = Inventariante.objects.all()
        html = render_to_string(
            "app_inventario/partials/inventariantes_list.html",
            {"inventariantes": inventariantes},
            request=request
        )

        # Retorna HTML + evento HTMX para fechar o modal
        response = HttpResponse(html)
        response.headers["HX-Trigger"] = "closeModal reloadInventariantes"

        return response

    return HttpResponse(status=405)


# ======= PATRIMÔNIO =======

@login_required
def patrimonio_list(request):
    """ Lista todos os patrimônios """
    patrimonios = Patrimonio.objects.all()
    return render(
        request,
        "app_inventario/patrimonio_list.html",
        {"patrimonios": patrimonios}
    )


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


@login_required
def patrimonio_add(request):
    """ Apenas exibe formulário de patrimônio """
    form = PatrimonioForm()
    return render(request, "app_inventario/form_patrimonio.html", {"form": form})


@login_required
def patrimonio_edit(request, pk):
    """ Edita patrimônio somente do próprio inventariante """
    inventariante = get_object_or_404(Inventariante, user=request.user)
    patrimonio = get_object_or_404(Patrimonio, pk=pk, inventariante=inventariante)

    if request.method == "POST":
        form = PatrimonioForm(request.POST, instance=patrimonio)

        if form.is_valid():
            form.save()

            patrimonios = Patrimonio.objects.filter(inventariante=inventariante)

            tabela = render_to_string(
                "app_inventario/partials/tabela_patrimonios.html",
                {"patrimonios": patrimonios},
                request=request
            )

            return HttpResponse(
                tabela,
                headers={"HX-Trigger": "patrimonio-atualizado"}
            )

        # Se erro, retorna formulário com mensagens
        html = render_to_string(
            "app_inventario/partials/form_patrimonio.html",
            {"form": form, "patrimonio": patrimonio},
            request=request
        )
        return HttpResponse(html)

    form = PatrimonioForm(instance=patrimonio)

    return render(
        request,
        "app_inventario/partials/form_patrimonio.html",
        {"form": form, "patrimonio": patrimonio}
    )


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
