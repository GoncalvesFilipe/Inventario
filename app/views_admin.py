from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import PatrimonioForm
from .models import Usuario, Patrimonio


# Página principal do painel
@login_required
def admin_dashboard(request):
    """Exibe o painel administrativo do usuário logado."""
    return render(request, "app_inventario/admin_dashboard.html")


# Listagem de usuários (somente do dono logado)
@login_required
def usuarios_list(request):
    """Lista apenas os usuários pertencentes ao dono logado."""
    usuarios = Usuario.objects.filter(owner=request.user).order_by("nome")
    return render(request, "app_inventario/partials/usuarios_list.html", {"usuarios": usuarios})


# Listagem de patrimônios (somente dos usuários do dono logado)
@login_required
def patrimonios_list(request):
    """Lista os patrimônios vinculados aos usuários do dono logado."""
    patrimonios = Patrimonio.objects.select_related("usuario").filter(usuario__owner=request.user)
    return render(request, "app_inventario/partials/patrimonio_list.html", {"patrimonios": patrimonios})


# Formulário de novo patrimônio
@login_required
def patrimonio_form(request):
    """Renderiza o formulário para adicionar um novo patrimônio"""
    if request.method == "POST":
        form = PatrimonioForm(request.POST)
        if form.is_valid():
            patrimonio = form.save(commit=False)

            # Garante que o usuário logado será associado ao patrimônio
            try:
                usuario_logado = Usuario.objects.get(owner=request.user)
            except Usuario.DoesNotExist:
                # Cria o vínculo automaticamente se ainda não existir
                usuario_logado = Usuario.objects.create(nome=request.user.username, owner=request.user)

            patrimonio.usuario = usuario_logado
            patrimonio.save()

            # Atualiza a lista após salvar
            patrimonios = Patrimonio.objects.select_related("usuario").filter(usuario__owner=request.user)
            tabela_html = render_to_string(
                "app_inventario/partials/tabela_patrimonios.html",
                {"patrimonios": patrimonios},
                request=request
            )
            return HttpResponse(tabela_html)

    else:
        form = PatrimonioForm()

    return render(request, "app_inventario/partials/form_patrimonio.html", {"form": form})

# Adicionar patrimônio
@login_required
def patrimonio_add(request):
    """Salva um novo patrimônio via HTMX"""
    if request.method == "POST":
        form = PatrimonioForm(request.POST)
        if form.is_valid():
            patrimonio = form.save(commit=False)
            patrimonio.usuario = Usuario.objects.get(owner=request.user)
            patrimonio.save()

            # Atualiza lista de patrimônios após salvar
            patrimonios = Patrimonio.objects.select_related("usuario").filter(usuario__owner=request.user)
            tabela_html = render_to_string(
                "app_inventario/partials/tabela_patrimonios.html",
                {"patrimonios": patrimonios},
                request=request
            )
            return HttpResponse(tabela_html)
        else:
            # Retorna o mesmo form com erros (HTMX mantém o modal aberto)
            html = render_to_string(
                "app_inventario/partials/form_patrimonio.html",
                {"form": form},
                request=request
            )
            return HttpResponse(html)

    # Requisição GET: renderiza o form vazio no modal
    form = PatrimonioForm()
    return render(request, "app_inventario/partials/form_patrimonio.html", {"form": form})


# Editar patrimônio
@login_required
def patrimonio_edit(request, pk):
    """Edita um patrimônio existente, apenas se pertencer ao dono logado."""
    patrimonio = get_object_or_404(Patrimonio, pk=pk)

    # Bloqueia acesso de outro usuário
    if patrimonio.usuario.owner != request.user:
        raise Http404

    if request.method == "POST":
        form = PatrimonioForm(request.POST, instance=patrimonio)
        if form.is_valid():
            form.save()

            # Atualiza a tabela após editar
            patrimonios = Patrimonio.objects.select_related("usuario").filter(usuario__owner=request.user)
            tabela_html = render_to_string(
                "app_inventario/partials/tabela_patrimonios.html",
                {"patrimonios": patrimonios},
                request=request
            )
            return HttpResponse(tabela_html)
        else:
            # Retorna o form com erros
            html = render_to_string(
                "app_inventario/partials/form_patrimonio.html",
                {"form": form, "patrimonio": patrimonio},
                request=request
            )
            return HttpResponse(html)

    # Requisição GET: exibe o form preenchido
    form = PatrimonioForm(instance=patrimonio)
    return render(request, "app_inventario/partials/form_patrimonio.html", {"form": form, "patrimonio": patrimonio})


# Confirma exclusão de patrimônio
@login_required
def confirmar_exclusao_patrimonio(request, pk):
    """Exibe o modal de confirmação antes de excluir o patrimônio."""
    patrimonio = get_object_or_404(Patrimonio, pk=pk, usuario__owner=request.user)
    return render(request, "app_inventario/partials/confirmar_exclusao_patrimonio.html", {"patrimonio": patrimonio})


# Excluir patrimônio
@login_required
@csrf_exempt
def excluir_patrimonio(request, pk):
    """Exclui um patrimônio via HTMX."""
    if request.method in ["POST", "DELETE"]:
        patrimonio = get_object_or_404(Patrimonio, pk=pk, usuario__owner=request.user)
        patrimonio.delete()

        patrimonios = Patrimonio.objects.select_related("usuario").filter(usuario__owner=request.user)
        return render(request, "app_inventario/partials/tabela_patrimonios.html", {"patrimonios": patrimonios})

    return HttpResponse(status=405)


# Editar usuário
@login_required
def usuario_edit(request, pk):
    """Edita um usuário pertencente ao dono logado."""
    usuario = get_object_or_404(Usuario, pk=pk, owner=request.user)

    if request.method == "POST":
        usuario.nome = request.POST.get("nome")
        usuario.funcao = request.POST.get("funcao")
        usuario.telefone = request.POST.get("telefone")
        usuario.save()

        usuarios = Usuario.objects.filter(owner=request.user).order_by("nome")
        return render(request, "app_inventario/partials/usuarios_list.html", {"usuarios": usuarios})

    return render(request, "app_inventario/partials/form_usuario.html", {"usuario": usuario})


# Excluir usuário
@login_required
def usuario_delete(request, pk):
    """Exclui um usuário pertencente ao dono logado."""
    usuario = get_object_or_404(Usuario, pk=pk, owner=request.user)

    if request.method == "POST":
        usuario.delete()
        usuarios = Usuario.objects.filter(owner=request.user).order_by("nome")
        return render(request, "app_inventario/partials/usuarios_list.html", {"usuarios": usuarios})

    return render(request, "app_inventario/partials/confirm_delete_usuario.html", {"usuario": usuario})


# Adicionar novo usuário
@login_required
def usuario_add(request):
    """Adiciona um novo usuário vinculado automaticamente ao dono logado."""
    if request.method == "POST":
        matricula = request.POST.get("matricula")
        nome = request.POST.get("nome")
        funcao = request.POST.get("funcao")
        telefone = request.POST.get("telefone")

        Usuario.objects.create(
            matricula=matricula,
            nome=nome,
            funcao=funcao,
            telefone=telefone,
            owner=request.user  # Garante vínculo com o usuário logado
        )

        usuarios = Usuario.objects.filter(owner=request.user).order_by("nome")
        return render(request, "app_inventario/partials/usuarios_list.html", {"usuarios": usuarios})

    return render(request, "app_inventario/partials/form_usuario_add.html")
