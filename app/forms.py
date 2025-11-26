from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Inventariante, Patrimonio


class InventarianteUserForm(UserCreationForm):
    """
    Formulário unificado para criar User + Inventariante.
    """

    matricula = forms.CharField(label="Matrícula", max_length=20)
    funcao = forms.CharField(label="Função/Cargo", max_length=50)
    telefone = forms.CharField(label="Telefone", max_length=15)
    presidente = forms.BooleanField(label="Presidente da Comissão", required=False)
    ano_atuacao = forms.IntegerField(label="Ano de Atuação", required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "matricula",
            "funcao",
            "telefone",
            "presidente",
            "ano_atuacao",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

            Inventariante.objects.create(
                user=user,
                matricula=self.cleaned_data["matricula"],
                funcao=self.cleaned_data["funcao"],
                telefone=self.cleaned_data["telefone"],
                presidente=self.cleaned_data["presidente"],
                ano_atuacao=self.cleaned_data["ano_atuacao"],
            )

        return user


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

        labels = {
            'patrimonio': 'Número do Patrimônio',
            'descricao': 'Descrição',
            'valor': 'Valor',
            'conta_contabil': 'Conta Contábil',
            'setor': 'Setor',
            'empenho': 'Empenho',
            'fornecedor': 'Fornecedor',
            'numero_documento': 'Nº do Documento',
            'data_documento': 'Data do Documento',
            'data_ateste': 'Data do Ateste',
            'dependencia': 'Dependência',
            'situacao': 'Situação',
            'observacoes': 'Observações',
            'data_inventario': 'Data do Inventário',
            'inventariante': 'Inventariante Responsável',
        }

        widgets = {
            "data_documento": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "data_ateste": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "data_inventario": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Aceita múltiplos formatos
        formatos_data = ["%Y-%m-%d", "%d/%m/%Y"]
        self.fields["data_documento"].input_formats = formatos_data
        self.fields["data_ateste"].input_formats = formatos_data
        self.fields["data_inventario"].input_formats = formatos_data

        # Filtra inventariante pelo user logado
        if user:
            try:
                inventariante = Inventariante.objects.get(user=user)
                self.fields["inventariante"].queryset = Inventariante.objects.filter(pk=inventariante.pk)
                self.fields["inventariante"].initial = inventariante

                # Campo apenas leitura
                self.fields["inventariante"].disabled = True
                self.fields["inventariante"].widget.attrs["readonly"] = True

            except Inventariante.DoesNotExist:
                self.fields["inventariante"].queryset = Inventariante.objects.none()