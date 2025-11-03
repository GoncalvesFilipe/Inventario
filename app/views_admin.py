from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Usuario, Patrimonio

# Página principal do painel
def admin_dashboard(request):
    return render(request, "app_inventario/admin_dashboard.html")

# Listagem dinâmica de usuários
def usuarios_list(request):
    usuarios = Usuario.objects.all().order_by("nome")
    return render(request, "app_inventario/partials/usuarios_list.html", {"usuarios": usuarios})

# Listagem dinâmica de patrimônios
def patrimonios_list(request):
    patrimonios = Patrimonio.objects.select_related("usuario").all()
    return render(request, "app_inventario/partials/patrimonio_list.html", {"patrimonios": patrimonios})

# Edição de usuário (carregada via HTMX)
def usuario_edit(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == "POST":
        usuario.nome = request.POST.get("nome")
        usuario.funcao = request.POST.get("funcao")
        usuario.telefone = request.POST.get("telefone")
        usuario.save()

        usuarios = Usuario.objects.all().order_by("nome")
        return render(request, "app_inventario/partials/usuarios_list.html", {"usuarios": usuarios})

    return render(request, "app_inventario/partials/form_usuario.html", {"usuario": usuario})

# Exclusão de usuário (carregada via HTMX)
def usuario_delete(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        usuario.delete()
        usuarios = Usuario.objects.all().order_by("nome")
        return render(request, "app_inventario/partials/usuarios_list.html", {"usuarios": usuarios})

    return render(request, "app_inventario/partials/confirm_delete_usuario.html", {"usuario": usuario})

# Adição de novo usuário (carregada via HTMX)
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
        )

        usuarios = Usuario.objects.all().order_by("nome")
        return render(request, "app_inventario/partials/usuarios_list.html", {"usuarios": usuarios})

    return render(request, "app_inventario/partials/form_usuario_add.html")
