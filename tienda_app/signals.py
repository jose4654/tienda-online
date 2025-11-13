from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomerProfile

User = get_user_model()


@receiver(post_save, sender=User)
def crear_perfil_para_usuario(sender, instance, created, **kwargs):
    """
    Genera de forma automática un perfil de cliente para cada usuario nuevo
    que no forme parte del personal de la tienda.
    """
    if created and not instance.is_staff:
        CustomerProfile.objects.create(user=instance, full_name=instance.get_full_name())

