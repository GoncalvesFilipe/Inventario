from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Inventariante

# Função disparada automaticamente após a criação de um objeto User.
@receiver(post_save, sender=User)
def criar_inventariante(sender, instance, created, **kwargs):
    """
    Cria automaticamente um registro de Inventariante associado ao novo usuário.
    - sender: modelo que emite o sinal (User).
    - instance: instância do usuário recém-criado.
    - created: indica se o objeto foi criado (True) ou apenas atualizado (False).
    - kwargs: argumentos adicionais do sinal.
    """
    if created:
        Inventariante.objects.create(user=instance)


# Função disparada automaticamente após a atualização de um objeto User.
@receiver(post_save, sender=User)
def salvar_inventariante(sender, instance, **kwargs):
    """
    Garante a persistência das alterações realizadas no inventariante
    vinculado ao usuário atualizado.
    - sender: modelo que emite o sinal (User).
    - instance: instância do usuário atualizado.
    - kwargs: argumentos adicionais do sinal.
    
    Caso o usuário não possua inventariante associado, a exceção é tratada
    silenciosamente para evitar falhas na execução.
    """
    try:
        instance.inventariante.save()
    except Inventariante.DoesNotExist:
        pass
