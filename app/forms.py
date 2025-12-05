from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Inventariante, Patrimonio

# FORMULÁRIO DE USUÁRIO + INVENTARIANTE (CRIAR / EDITAR)
class InventarianteUserForm(forms.ModelForm):
    """
    Formulário unificado para criar e editar User + Inventariante.
    """

    # -------- Campos adicionais do Inventariante --------
    matricula = forms.CharField(label="Matrícula", max_length=20)
    funcao = forms.CharField(label="Função/Cargo", max_length=50)
    telefone = forms.CharField(label="Telefone", max_length=15)
    presidente = forms.BooleanField(label="Presidente da Comissão", required=False)
    ano_atuacao = forms.IntegerField(label="Ano de Atuação", required=False)

    # -------- Campos de Senha --------
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput,
        required=False
    )
    password2 = forms.CharField(
        label="Confirme a Senha",
        widget=forms.PasswordInput,
        required=False
    )

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

    # ---------------- Validação ----------------
    def clean(self):
        cleaned = super().clean()

        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")

        # Cadastro novo
        if not self.instance.pk:
            if not p1 or not p2:
                raise forms.ValidationError("As senhas são obrigatórias para novo usuário.")
            if p1 != p2:
                raise forms.ValidationError("As senhas não coincidem.")

        # Edição
        else:
            if p1 or p2:
                if p1 != p2:
                    raise forms.ValidationError("As senhas não coincidem.")

        return cleaned

    # ---------------- Salvamento ----------------
    def save(self, commit=True):
        user = super().save(commit=False)

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]

        # Atualizar senha (apenas se digitada)
        p1 = self.cleaned_data.get("password1")
        if p1:
            user.password = make_password(p1)

        if commit:
            user.save()

            # Criar ou atualizar Inventariante
            inventariante, created = Inventariante.objects.get_or_create(user=user)

            inventariante.matricula = self.cleaned_data["matricula"]
            inventariante.funcao = self.cleaned_data["funcao"]
            inventariante.telefone = self.cleaned_data["telefone"]
            inventariante.presidente = self.cleaned_data["presidente"]
            inventariante.ano_atuacao = self.cleaned_data["ano_atuacao"]

            inventariante.save()

        return user


# FORMULÁRIO DE PATRIMÔNIO
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

        # Aceita múltiplos formatos de data
        formatos_data = ["%Y-%m-%d", "%d/%m/%Y"]
        self.fields["data_documento"].input_formats = formatos_data
        self.fields["data_ateste"].input_formats = formatos_data
        self.fields["data_inventario"].input_formats = formatos_data

        # Filtrar inventariante pelo usuário logado
        if user:
            try:
                inventariante = Inventariante.objects.get(user=user)
                self.fields["inventariante"].queryset = Inventariante.objects.filter(pk=inventariante.pk)
                self.fields["inventariante"].initial = inventariante

                # Campo somente leitura
                self.fields["inventariante"].disabled = True
                self.fields["inventariante"].widget.attrs["readonly"] = True

            except Inventariante.DoesNotExist:
                self.fields["inventariante"].queryset = Inventariante.objects.none()
