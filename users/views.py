from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from app.forms import InventarianteUserForm

#  REGISTRO (User + Inventariante)
def register_view(request):
    """
    Cadastro unificado:
    - Cria User
    - Cria Inventariante vinculado via OneToOne
    """

    if request.method == "POST":
        form = InventarianteUserForm(request.POST)

        if form.is_valid():
            # O MÉTODO save() DO FORM JÁ:
            # - cria User
            # - cria Inventariante
            user = form.save()

            # Login automático após o cadastro
            login(request, user)

            # Caso seja requisição HTMX → retorna somente o conteudo
            if request.headers.get("HX-Request"):
                return HttpResponse(
                    "<p class='text-success fw-bold'>Cadastro concluído com sucesso!</p>"
                )

            return redirect("index")  # usuário já logado

        # Se houver erro e for HTMX → devolve apenas o formulário
        if request.headers.get("HX-Request"):
            return render(request, "users/register.html", {"form": form})

    else:
        form = InventarianteUserForm()

    return render(request, "users/register.html", {"form": form})


#  LOGIN
def login_view(request):
    """
    Tela de login tradicional usando AuthenticationForm
    """

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Redirecionamento após login
            next_url = request.POST.get("next") or "index"
            return redirect(next_url)

        # Erro via HTMX
        if request.headers.get("HX-Request"):
            return render(request, "users/login.html", {"form": form})

    else:
        form = AuthenticationForm()

    return render(request, "users/login.html", {"form": form})


#  LOGOUT
def logout_view(request):
    """
    Finaliza sessão e envia usuário ao login
    """
    logout(request)
    return redirect("login")
