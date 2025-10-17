from django import forms
from .models import Usuario, Patrimonio

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'matricula',
            'nome',
            'funcao',
            'telefone',
            'email',
            'presidente',
            'ano_atuacao',
        ]
        labels = {
            'matricula': 'Matrícula',
            'nome': 'Nome',
            'funcao': 'Cargo/Função',
            'telefone': 'Telefone',
            'email': 'E-mail',
            'presidente': 'Presidente',
            'ano_atuacao': 'Ano de Atuação',
        }


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
            'usuario',
        ]
        labels = {
            'patrimonio': 'Nome do Patrimônio',
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
            'usuario': 'Inventariante Responsável',
            }