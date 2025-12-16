from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from app.forms import InventarianteUserForm

#  REGISTRO (User + Inventariante)
def register_view(request):
    """ 
    Fluxo HTMX:
    
    - Retorna mensagem de sucesso
    - Modal se fecha após 3s
    - Redireciona para login
    """

    if request.method == "POST":
        form = InventarianteUserForm(request.POST)

        if form.is_valid():
            user = form.save()

            # NÃO faz login automático
            # porque o destino final será a tela de login

            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "users/partials/register_success.html"
                )

            return redirect("login")

        if request.headers.get("HX-Request"):
            return render(
                request,
                "users/partials/register_form.html",
                {"form": form}
            )

    form = InventarianteUserForm()
    return render(
        request,
        "users/partials/register_form.html",
        {"form": form}
    )


#  LOGIN
def login_view(request):
    """
    Autenticação de usuário.
    Compatível com requisição normal e HTMX.
    """

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            login(request, form.get_user())
            return redirect(request.POST.get("next") or "index")

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
