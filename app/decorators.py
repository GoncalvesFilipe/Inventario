from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):

        is_presidente = (
            hasattr(request.user, "inventariante")
            and request.user.inventariante.presidente
        )

        # Usuário sem permissão
        if not request.user.is_superuser and not is_presidente:

            # --- Requisição HTMX (modal) ---
            if request.headers.get("HX-Request"):
                html = render(
                    request,
                    "app_inventario/modals/modal_acesso_negado.html"
                )
                # Retorna 200 para o HTMX abrir o modal corretamente
                return HttpResponse(html.content)

            # --- Requisição normal (fora do HTMX) ---
            html = render(
                request,
                "app_inventario/modals/modal_acesso_negado.html"
            )
            return HttpResponseForbidden(html.content)

        return view_func(request, *args, **kwargs)

    return wrapper

def presidente_ou_superuser(user): return ( user.is_authenticated and ( user.is_superuser or user.groups.filter(name="Presidente").exists() ) )