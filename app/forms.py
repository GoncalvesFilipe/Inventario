from django import forms
from django.contrib.auth.models import User
from .models import Inventariante, Patrimonio


class InventarianteForm(forms.ModelForm):
    """Formulário para dados extras do inventariante."""
    
    # Campos pertencentes ao User
    first_name = forms.CharField(label="Nome", max_length=150)
    last_name = forms.CharField(label="Sobrenome", max_length=150)
    email = forms.EmailField(label="E-mail")

    class Meta:
        model = Inventariante
        fields = [
            'matricula',
            'funcao',
            'telefone',
            'presidente',
            'ano_atuacao',
        ]
        labels = {
            'matricula': 'Matrícula',
            'funcao': 'Função/Cargo',
            'telefone': 'Telefone',
            'presidente': 'Presidente da Comissão',
            'ano_atuacao': 'Ano de Atuação',
        }

    # Salvando User + Inventariante juntos
    def save(self, commit=True):
        inventariante = super().save(commit=False)

        # Criando ou atualizando o usuário Django
        if inventariante.pk:
            user = inventariante.user  # já existe
        else:
            user = User()

        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            inventariante.user = user
            inventariante.save()

        return inventariante

class PatrimonioForm(forms.ModelForm):
    class Meta:
        model = Patrimonio
        fields = [
            "patrimonio", "descricao", "valor", "conta_contabil",
            "setor", "empenho", "fornecedor", "numero_documento",
            "data_documento", "data_ateste", "dependencia",
            "situacao", "observacoes", "data_inventario",
            "inventariante",
        ]

        widgets = {
            "data_documento": forms.DateInput(attrs={"type": "date"}),
            "data_ateste": forms.DateInput(attrs={"type": "date"}),
            "data_inventario": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        """
        - Filtra o campo inventariante para exibir apenas o inventariante do usuário logado
        - Impede edição desse campo deixando ele fixo
        """
        super().__init__(*args, **kwargs)

        if user:
            try:
                inventariante = Inventariante.objects.get(user=user)
                self.fields["inventariante"].queryset = Inventariante.objects.filter(pk=inventariante.pk)
                self.fields["inventariante"].initial = inventariante
                self.fields["inventariante"].widget.attrs["readonly"] = True
                self.fields["inventariante"].disabled = True
            except Inventariante.DoesNotExist:
                # Caso o usuário não seja inventariante
                self.fields["inventariante"].queryset = Inventariante.objects.none()
