# ==========================================================
# HELPER DE PERMISSÃO
# ----------------------------------------------------------
# Função usada em decorators para restringir acesso às views
# apenas a superusuários ou inventariantes presidentes.
# ==========================================================
def presidente_ou_superuser(user):
    """Retorna True se o usuário for superusuário ou inventariante presidente."""
    if user.is_superuser:
        return True
    if hasattr(user, "inventariante") and user.inventariante.presidente:
        return True
    return False
