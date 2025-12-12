from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Inventariante, Patrimonio


# FORMULÁRIO DE USUÁRIO + INVENTARIANTE (CRIAR / EDITAR)
class InventarianteUserForm(forms.ModelForm):
    """
    Formulário unificado para criar e editar User + Inventariante.
    """

    # -------- Campos do User --------
    username = forms.CharField(label="Usuário")
    first_name = forms.CharField(label="Nome")
    last_name = forms.CharField(label="Sobrenome")
    email = forms.EmailField(label="E-mail")

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
        model = Inventariante
        fields = [
            "matricula",
            "funcao",
            "telefone",
            "presidente",
            "ano_atuacao",
        ]

    # ---------------- Inicialização ----------------
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_instance = user

        if user:
            self.fields["username"].initial = user.username
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email

    # ---------------- Validação ----------------
    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")

        if not self.user_instance or not self.user_instance.pk:
            # Cadastro novo
            if not p1 or not p2:
                raise forms.ValidationError("As senhas são obrigatórias para novo usuário.")
            if p1 != p2:
                raise forms.ValidationError("As senhas não coincidem.")
        else:
            # Edição
            if p1 or p2:
                if p1 != p2:
                    raise forms.ValidationError("As senhas não coincidem.")

        return cleaned

    def clean_matricula(self):
        matricula = self.cleaned_data.get("matricula")
        qs = Inventariante.objects.filter(matricula=matricula)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("Já existe um inventariante com esta matrícula.")

        return matricula

    # ---------------- Salvamento ----------------
    def save(self, commit=True):
        inventariante = super().save(commit=False)
        user = self.user_instance

        # Atualizar dados do User
        user.username = self.cleaned_data["username"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]

        p1 = self.cleaned_data.get("password1")
        if p1:
            user.password = make_password(p1)

        if commit:
            user.save()
            inventariante.user = user
            inventariante.save()

        return inventariante


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
