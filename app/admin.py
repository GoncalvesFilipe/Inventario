from django.contrib import admin
from .models import Inventariante, Patrimonio

# ==========================================================
# REGISTRO DE INVENTARIANTE NO ADMIN
# ----------------------------------------------------------
# Configurações da interface administrativa para o modelo
# Inventariante.
# ==========================================================
@admin.register(Inventariante)
class InventarianteAdmin(admin.ModelAdmin):
    """Administração do modelo Inventariante."""
    list_display = ["user", "matricula", "funcao", "telefone", "presidente"]
    search_fields = ["user__username", "user__first_name", "user__last_name", "matricula"]


# ==========================================================
# REGISTRO DE PATRIMÔNIO NO ADMIN
# ----------------------------------------------------------
# Configurações da interface administrativa para o modelo
# Patrimonio.
# ==========================================================
@admin.register(Patrimonio)
class PatrimonioAdmin(admin.ModelAdmin):
    """Administração do modelo Patrimonio."""
    list_display = ["tombo", "descricao", "setor", "situacao", "inventariante"]
    search_fields = ["tombo", "descricao", "setor", "inventariante__user__username"]
    list_filter = ["situacao", "setor", "conta_contabil"]
