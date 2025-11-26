from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Inventariante, Patrimonio


class InventarianteUserForm(UserCreationForm):
    """
    Formulário unificado para criar User + Inventariante.
    Estende UserCreationForm e adiciona todos os campos extras do Inventariante.
    """

    # Campos extras do modelo Inventariante
    matricula = forms.CharField(label="Matrícula", max_length=20)
    funcao = forms.CharField(label="Função/Cargo", max_length=50)
    telefone = forms.CharField(label="Telefone", max_length=15)
    presidente = forms.BooleanField(label="Presidente da Comissão", required=False)
    ano_atuacao = forms.IntegerField(label="Ano de Atuação", required=False)

    class Meta:
        """
        User será criado normalmente, mas os demais campos adicionais
        serão utilizados para criar a instância de Inventariante.
        """
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
        """
        Sobrescrita do método save():
        - Cria o User normalmente
        - Em seguida cria a tabela Inventariante associada ao User
        """
        # Criando o user sem salvar ainda (para adicionar campos extras antes)
        user = super().save(commit=False)

        # Atualizando campos do User
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]

        # Salvando User
        if commit:
            user.save()

            # Criando Inventariante vinculado ao user
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
    """ Formulário padrão para cadastro de patrimônio """

    class Meta:
        model = Patrimonio
        fields = [
            'patrimonio',
            'descricao',
            'valor',
            'conta_contabil',
            'setor',
            'empenho',
            'fornecedor',
            'numero_documento',
            'data_documento',
            'data_ateste',
            'dependencia',
            'situacao',
            'observacoes',
            'data_inventario',
            'inventariante',
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
