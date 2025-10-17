from django.shortcuts import render

# PÁGINA INICIAL DO SITE
def index(request):
    return render(request, "app_inventario/index.html")  # Renderiza o template da página inicial
