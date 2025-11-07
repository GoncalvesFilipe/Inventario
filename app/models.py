from django.db import models
from django.contrib.auth.models import User

class Usuario(models.Model):
  matricula = models.CharField(max_length=20, verbose_name='Matricula', unique=True)
  nome = models.CharField(max_length=100)
  funcao = models.CharField(max_length=50)
  telefone = models.CharField(max_length=15)
  email = models.EmailField(blank=True, null=True)
  presidente = models.BooleanField(default=True)
  data_cadastro = models.DateField(auto_now_add=True)
  data_atualizacao = models.DateTimeField(auto_now=True)
  ano_atuacao = models.PositiveBigIntegerField(verbose_name='Ano de atuação', unique=True, blank=True, null=True)
  owner = models.ForeignKey(User, on_delete=models.CASCADE)

  def __str__(self):
        return f"{self.nome} ({self.matricula})"
  
class Patrimonio(models.Model):

  STATUS_CHOICES = [
        ('localizado', 'Localizado'),
        ('nao_localizado', 'Não Localizado'),
        ('calamidade', 'Perda por Calamidade'),
    ]

  patrimonio = models.IntegerField('Patrimonio', unique=True)
  descricao = models.TextField(blank=True, null=True)
  valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
  conta_contabil = models.CharField(max_length=50, blank=True, null=True)
  setor = models.CharField(max_length=100, blank=True, null=True)
  empenho = models.CharField(max_length=50, blank=True, null=True)
  fornecedor = models.CharField(max_length=100, blank=True, null=True)
  numero_documento = models.CharField(max_length=50, blank=True, null=True)
  data_documento = models.DateField(blank=True, null=True)
  data_ateste = models.DateField(blank=True, null=True)
  dependencia = models.CharField(max_length=100, blank=True, null=True)
  situacao = models.CharField(max_length=20, choices=STATUS_CHOICES, default='localizado')
  observacoes = models.TextField(blank=True, null=True)
  data_inventario = models.DateField(blank=True, null=True)

  # Relacionamento 1 para 1 com Usuario
  usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='patrimonio')
  
  def __str__(self):
    return f"{self.patrimonio} ({self.usuario.nome})"
  
