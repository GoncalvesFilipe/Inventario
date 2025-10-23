from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages


def logout_view(request):
    """Faz um logout do usuário"""
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def login_view(request):
    """Exibe e processa o formulário de login."""
    
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            messages.error(request, "Usuário ou senha inválidos.")
            return render(request, 'users/login.html')
    
    return render(request, 'users/login.html')


def register(request):
    """Faz o cadastro de um novo usuário."""
    
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    
    if request.method != 'POST':
        # Exibe o formulário de cadastro em branco.
        form = UserCreationForm()
    else:
        # Processa o formulário preenchido.
        form = UserCreationForm(data=request.POST)
        
        if form.is_valid():
            new_user = form.save()
            # Faz login do usuário e o redireciona para a página inicial.
            authenticated_user = authenticate(
                username=new_user.username, 
                password=request.POST['password1']
            )
            login(request, authenticated_user)
            return HttpResponseRedirect(reverse('index'))
    
    context = {'form': form}
    return render(request, 'users/register.html', context)
