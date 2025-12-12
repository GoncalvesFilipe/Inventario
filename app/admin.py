from django.contrib import admin
from .models import Inventariante, Patrimonio

# Registro do modelo Inventariante na interface administrativa do Django.
@admin.register(Inventariante)
class InventarianteAdmin(admin.ModelAdmin):
    """ - list_display: define os campos que serão exibidos na lista de registros.
        - search_fields: permite a busca por atributos específicos do inventariante."""
    list_display = ["user", "matricula", "funcao", "telefone", "presidente"]
    search_fields = ["user__username", "user__first_name", "user__last_name", "matricula"]


# Registro do modelo Patrimonio na interface administrativa do Django.
@admin.register(Patrimonio)
class PatrimonioAdmin(admin.ModelAdmin):
    """ - list_display: define os campos que serão exibidos na lista de registros.
        - search_fields: permite a busca por atributos específicos do patrimônio."""
    list_display = ["patrimonio", "inventariante", "setor", "situacao"]
    search_fields = ["patrimonio", "inventariante__user__username"]
