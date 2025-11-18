from django.contrib import admin
from .models import Inventariante, Patrimonio

@admin.register(Inventariante)
class InventarianteAdmin(admin.ModelAdmin):
    list_display = ["user", "matricula", "funcao", "telefone", "presidente"]
    search_fields = ["user__username", "user__first_name", "user__last_name", "matricula"]

@admin.register(Patrimonio)
class PatrimonioAdmin(admin.ModelAdmin):
    list_display = ["patrimonio", "inventariante", "setor", "situacao"]
    search_fields = ["patrimonio", "inventariante__user__username"]
