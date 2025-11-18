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
