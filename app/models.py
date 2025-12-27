from django.db import models
from django.contrib.auth.models import User


class Inventariante(models.Model):
    """Modelo que armazena informações complementares sobre o inventariante."""

    # Relaciona cada inventariante a um usuário do sistema (1:1).
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="inventariante")

    # Identificação funcional única do inventariante.
    matricula = models.CharField(max_length=20, verbose_name='Matrícula', unique=True)

    # Função ou cargo desempenhado pelo inventariante.
    funcao = models.CharField(max_length=50)

    # Número de telefone para contato.
    telefone = models.CharField(max_length=15)

    # Indica se o inventariante exerce a função de presidente.
    presidente = models.BooleanField(default=False)

    # Data de criação automática do registro.
    data_cadastro = models.DateField(auto_now_add=True)

    # Data de atualização automática do registro.
    data_atualizacao = models.DateTimeField(auto_now=True)

    # Ano de atuação do inventariante, opcional.
    ano_atuacao = models.PositiveBigIntegerField(
        verbose_name='Ano de atuação',
        blank=True,
        null=True
    )

    def __str__(self):
        """Retorna representação textual do inventariante, exibindo nome e matrícula."""
        return f"{self.user.get_full_name() or self.user.username} ({self.matricula})"


class Patrimonio(models.Model):
    """Modelo que representa bens patrimoniais vinculados ao inventário."""

    # ==========================================================
    # CONJUNTO DE OPÇÕES DE SITUAÇÃO
    # ----------------------------------------------------------
    # Define os estados possíveis de um patrimônio:
    # - Localizado
    # - Não Localizado
    # - Perda por Calamidade
    # ==========================================================
    STATUS_CHOICES = [
        ('localizado', 'Localizado'),
        ('nao_localizado', 'Não Localizado'),
        ('calamidade', 'Perda por Calamidade'),
    ]

    # Número identificador único do patrimônio (tombo).
    tombo = models.IntegerField('tombo', unique=True, null=True, blank=True)

    # Descrição detalhada do bem.
    descricao = models.TextField(blank=True, null=True)

    # Valor monetário do patrimônio.
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Conta contábil associada ao bem.
    conta_contabil = models.CharField(max_length=50, blank=True, null=True)

    # Setor responsável ou local de alocação do patrimônio.
    setor = models.CharField(max_length=100, blank=True, null=True)

    # Número de empenho relacionado à aquisição.
    empenho = models.CharField(max_length=50, blank=True, null=True)

    # Nome do fornecedor do bem.
    fornecedor = models.CharField(max_length=100, blank=True, null=True)

    # Documento fiscal ou administrativo associado.
    numero_documento = models.CharField(max_length=50, blank=True, null=True)

    # Data de emissão do documento.
    data_documento = models.DateField(blank=True, null=True)

    # Data de ateste ou conferência do bem.
    data_ateste = models.DateField(blank=True, null=True)

    # Dependência ou unidade administrativa vinculada.
    dependencia = models.CharField(max_length=100, blank=True, null=True)

    # Situação atual do patrimônio, conforme opções definidas.
    situacao = models.CharField(max_length=20, choices=STATUS_CHOICES, default='localizado')

    # Observações adicionais sobre o bem.
    observacoes = models.TextField(blank=True, null=True)

    # Data em que o bem foi inventariado.
    data_inventario = models.DateField(blank=True, null=True)

    # Relação com o inventariante responsável pelo patrimônio.
    inventariante = models.ForeignKey(
        Inventariante,
        on_delete=models.CASCADE,
        related_name='patrimonios'
    )

    # ==========================================================
    # REPRESENTAÇÃO TEXTUAL
    # ----------------------------------------------------------
    # Retorna uma string amigável para identificar o patrimônio
    # exibindo o tombo e o inventariante associado.
    # ==========================================================
    def __str__(self):
        return f"{self.tombo} ({self.inventariante.user.get_full_name() or self.inventariante.user.username})"


class RegistroPlanilha(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="registros_planilha"
    )
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.descricao} - {self.usuario.username}"