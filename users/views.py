from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from app.models import Usuario

@login_required
def logout_view(request):
    """Faz logout do usuário autenticado."""
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def register(request):
    """Faz o cadastro de um novo usuário e cria o registro correspondente em Usuario."""
    
    # 🔒 Se o usuário já estiver autenticado, impede novo cadastro
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    
    if request.method != 'POST':
        # Exibe o formulário de cadastro em branco
        form = UserCreationForm()
    else:
        # Processa o formulário enviado
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            # Salva o novo usuário Django
            new_user = form.save()

            # 🔒 Cria automaticamente um registro "Usuario" vinculado ao usuário Django
            Usuario.objects.create(
                matricula=f"MAT-{new_user.id}",  # Pode ajustar conforme sua lógica
                nome=new_user.username,
                funcao="Não definida",
                telefone="",
                owner=new_user
            )

            # Autentica e faz login automaticamente
            authenticated_user = authenticate(
                username=new_user.username, 
                password=request.POST['password1']
            )
            login(request, authenticated_user)

            # Redireciona para a página inicial
            return HttpResponseRedirect(reverse('index'))

    context = {'form': form}
    return render(request, 'users/register.html', context)
