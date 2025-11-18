from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Inventariante

@receiver(post_save, sender=User)
def criar_inventariante(sender, instance, created, **kwargs):
    if created:
        Inventariante.objects.create(user=instance)

@receiver(post_save, sender=User)
def salvar_inventariante(sender, instance, **kwargs):
    try:
        instance.inventariante.save()
    except Inventariante.DoesNotExist:
        pass
