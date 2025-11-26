from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


# VIEW DE REGISTRO
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Autentica e faz login automaticamente
            login(request, user)

            # Se a requisição veio pelo HTMX:
            if request.headers.get("HX-Request"):
                return HttpResponse("<p class='text-success'>Usuário registrado com sucesso!</p>")

            return redirect("login")
        else:
            # Retorna somente o formulário para substituir via HTMX
            if request.headers.get("HX-Request"):
                return render(request, "users/register.html", {"form": form})

    else:
        form = UserCreationForm()

    return render(request, "users/register.html", {"form": form})


# VIEW DE LOGIN 
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if request.headers.get("HX-Request"):
                return HttpResponse("<p class='text-success'>Login realizado com sucesso!</p>")

            return redirect("painel_admin")  # redirecione para o painel correto

        else:
            if request.headers.get("HX-Request"):
                return render(request, "users/login.html", {"form": form})

    else:
        form = AuthenticationForm()

    return render(request, "users/login.html", {"form": form})


# VIEW DE LOGOUT
@login_required
def logout_view(request):
    logout(request)

    # Caso seja logout via HTMX, devolve um fragmento atualizado
    if request.headers.get("HX-Request"):
        return HttpResponse("<p class='text-info'>Você saiu do sistema.</p>")

    return redirect("login")
