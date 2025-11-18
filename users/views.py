from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from app.models import Inventariante


@login_required
def logout_view(request):
    """Faz logout do usuário autenticado."""
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def register(request):
    """Registra novo usuário Django e cria o Inventariante vinculado."""

    # Se já está autenticado, não pode registrar novo usuário
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

    if request.method != 'POST':
        form = UserCreationForm()
    else:
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            # Cria o usuário Django
            new_user = form.save()

            # ⚠️ IMPORTANTE:
            # Cria automaticamente um Inventariante vinculado ao usuário Django
            Inventariante.objects.create(
                user=new_user,              # vínculo correto
                nome=new_user.username,     # pode ser substituído depois
                matricula=f"INV-{new_user.id}",
                funcao="Não definida",
                telefone=""
            )

            # Autentica e faz login
            authenticated_user = authenticate(
                username=new_user.username,
                password=request.POST['password1']
            )
            login(request, authenticated_user)

            return HttpResponseRedirect(reverse('index'))

    context = {'form': form}
    return render(request, 'users/register.html', context)
