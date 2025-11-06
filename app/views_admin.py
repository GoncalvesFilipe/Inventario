from django.shortcuts import render, get_object_or_404
from .forms import PatrimonioForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Usuario, Patrimonio
from django.contrib.auth.decorators import login_required

# Página principal do painel
def admin_dashboard(request):
    return render(request, "app_inventario/admin_dashboard.html")

# Listagem dinâmica de usuários (somente do dono logado)
@login_required
def usuarios_list(request):
    usuarios = Usuario.objects.filter(owner=request.user).order_by("nome")
    return render(request, "app_inventario/partials/usuarios_list.html", {"usuarios": usuarios})

# Listagem de patrimônios (filtrados pelos usuários do dono)
@login_required
def patrimonios_list(request):
    patrimonios = Patrimonio.objects.select_related("usuario").filter(usuario__owner=request.user)
    return render(request, "app_inventario/partials/patrimonio_list.html", {"patrimonios": patrimonios})

# Exibir formulário de novo patrimônio
@login_required
def patrimonio_form(request):
    if request.method == "POST":
        form = PatrimonioForm(request.POST)
        if form.is_valid():
            form.save()
            patrimonios = Patrimonio.objects.filter(usuario__owner=request.user)
            return render(request, "app_inventario/partials/tabela_patrimonios.html", {"patrimonios": patrimonios})
    else:
        form = PatrimonioForm()
    
    return render(request, "app_inventario/partials/form_patrimonio.html", {"form": form})

# Adicionar patrimônio
@login_required
def patrimonio_add(request):
    if request.method == "POST":
        form = PatrimonioForm(request.POST)
        if form.is_valid():
            form.save()

            patrimonios = Patrimonio.objects.select_related("usuario").filter(usuario__owner=request.user)
            tabela_html = render_to_string(
                "app_inventario/partials/tabela_patrimonios.html",
                {"patrimonios": patrimonios},
                request=request
            )

            html_final = (
                tabela_html
                + '<div id="form-patrimonio-container" hx-swap-oob="true"></div>'
            )

            return render(request, "app_inventario/partials/form_patrimonio.html", {"form": form})

# Editar patrimônio
@login_required
def patrimonio_edit(request, pk):
    patrimonio = get_object_or_404(Patrimonio, pk=pk, usuario__owner=request.user)
    if request.method == "POST":
        form = PatrimonioForm(request.POST, instance=patrimonio)
        if form.is_valid():
            form.save()
            patrimonios = Patrimonio.objects.filter(usuario__owner=request.user)
            return render(request, "app_inventario/partials/tabela_patrimonios.html", {"patrimonios": patrimonios})
    else:
        form = PatrimonioForm(instance=patrimonio)

    return render(
        request,
        "app_inventario/partials/form_patrimonio.html",
        {"form": form, "patrimonio": patrimonio}
    )

# Edição de usuário (somente os que pertencem ao dono logado)
@login_required
def usuario_edit(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk, owner=request.user)

    if request.method == "POST":
        usuario.nome = request.POST.get("nome")
        usuario.funcao = request.POST.get("funcao")
        usuario.telefone = request.POST.get("telefone")
        usuario.save()

        usuarios = Usuario.objects.filter(owner=request.user).order_by("nome")
        return render(request, "app_inventario/partials/usuarios_list.html", {"usuarios": usuarios})

    return render(request, "app_inventario/partials/form_usuario.html", {"usuario": usuario})

# Exclusão de usuário (somente os do dono logado)
@login_required
def usuario_delete(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk, owner=request.user)

    if request.method == 'POST':
        usuario.delete()
        usuarios = Usuario.objects.filter(owner=request.user).order_by("nome")
        return render(request, "app_inventario/partials/usuarios_list.html", {"usuarios": usuarios})

    return render(request, "app_inventario/partials/confirm_delete_usuario.html", {"usuario": usuario})

# Adição de novo usuário (vincula automaticamente ao dono logado)
@login_required
def usuario_add(request):
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
            owner=request.user  # 🔥 Define o dono aqui
        )

        usuarios = Usuario.objects.filter(owner=request.user).order_by("nome")
        return render(request, "app_inventario/partials/usuarios_list.html", {"usuarios": usuarios})

    return render(request, "app_inventario/partials/form_usuario_add.html")
