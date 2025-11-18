from django.db import models
from django.contrib.auth.models import User


class Inventariante(models.Model):
  """Informações adicionais do inventariante."""
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="inventariante")
  matricula = models.CharField(max_length=20, verbose_name='Matrícula', unique=True)
  funcao = models.CharField(max_length=50)
  telefone = models.CharField(max_length=15)
  email = models.EmailField(blank=True, null=True)
  presidente = models.BooleanField(default=True)
  data_cadastro = models.DateField(auto_now_add=True)
  data_atualizacao = models.DateTimeField(auto_now=True)
  ano_atuacao = models.PositiveBigIntegerField(
    verbose_name='Ano de atuação',
    unique=True,
    blank=True,
    null=True
  )

  def __str__(self):
    return f"{self.user.get_full_name() or self.user.username} ({self.matricula})"
  
class Patrimonio(models.Model):
  
  STATUS_CHOICES = [
    ('localizado', 'Localizado'),
    ('nao_localizado', 'Não Localizado'),
    ('calamidade', 'Perda por Calamidade'),
  ]

  patrimonio = models.IntegerField('Patrimônio', unique=True)
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

  # O patrimônio pertence a um Inventariante
  inventariante = models.ForeignKey(
    Inventariante,
    on_delete=models.CASCADE,
    related_name='patrimonios'
  )

  def __str__(self):
    return f"{self.patrimonio} ({self.inventariante.user.get_full_name() or self.inventariante.user.username})"
