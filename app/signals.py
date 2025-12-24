from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Inventariante

# -------------------------------------------------------------------
# SIGNAL: Criar Inventariante automaticamente ao criar um novo User
# -------------------------------------------------------------------
@receiver(post_save, sender=User)
def criar_inventariante(sender, instance, created, **kwargs):
    """
    Dispara sempre que um objeto User é salvo.
    
    Objetivo:
    - Criar automaticamente um registro de Inventariante vinculado ao novo usuário.
    - Se o usuário for superusuário, define valores padrão específicos.
    
    Parâmetros:
    - sender: modelo que emite o sinal (User).
    - instance: instância do usuário recém-criado.
    - created: indica se o objeto foi criado (True) ou apenas atualizado (False).
    - kwargs: argumentos adicionais do sinal.
    """
    if created:
        # Se for superusuário, cria Inventariante com valores padrão
        if instance.is_superuser:
            Inventariante.objects.get_or_create(
                user=instance,
                defaults={
                    "matricula": "0000",
                    "funcao": "Administrador",
                    "telefone": "",
                    "presidente": False,
                }
            )
        else:
            # Usuário comum → cria Inventariante simples
            Inventariante.objects.create(
                user=instance,
                matricula=f"USR-{instance.pk}",  # exemplo de matrícula gerada
                funcao="Colaborador",
                telefone="",
                presidente=False,
            )


# -------------------------------------------------------------------
# SIGNAL: Salvar Inventariante ao atualizar um User
# -------------------------------------------------------------------
@receiver(post_save, sender=User)
def salvar_inventariante(sender, instance, **kwargs):
    """
    Dispara sempre que um objeto User é atualizado.
    
    Objetivo:
    - Garantir que o Inventariante vinculado ao usuário também seja salvo.
    - Se o usuário não possuir Inventariante associado, trata a exceção
      silenciosamente para evitar falhas.
    
    Parâmetros:
    - sender: modelo que emite o sinal (User).
    - instance: instância do usuário atualizado.
    - kwargs: argumentos adicionais do sinal.
    """
    try:
        instance.inventariante.save()
    except Inventariante.DoesNotExist:
        # Nenhum inventariante vinculado → ignora
        pass
