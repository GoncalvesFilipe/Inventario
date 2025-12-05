
from functools import wraps
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import render_to_string

def admin_required(function):
    """
    Permite acesso apenas a usuários admin (is_staff=True).
    Se for HTMX e o usuário não puder, retorna um modal.
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return HttpResponseForbidden("Usuário não autenticado.")

        if not request.user.is_staff:

            # Se for HTMX, retorna modal de erro
            if request.headers.get("HX-Request"):
                html = render_to_string("modals/erro_permissao.html")
                response = HttpResponse(html)
                response["HX-Retarget"] = "#modal-area"
                response["HX-Reswap"] = "innerHTML"
                return response

            # Se for acesso normal, retorna Forbidden
            return HttpResponseForbidden("Acesso negado.")

        return function(request, *args, **kwargs)

    return wrap
