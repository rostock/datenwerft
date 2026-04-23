from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models.base import Provider
from .models.services import ServiceImage


@receiver(pre_save, sender=Provider)
def delete_old_logo_on_change(sender, instance, **kwargs):
  if not instance.pk:
    return
  try:
    old_logo = Provider.objects.get(pk=instance.pk).logo
  except Provider.DoesNotExist:
    return
  new_logo = instance.logo
  if old_logo and old_logo != new_logo:
    old_logo.delete(save=False)


@receiver(post_delete, sender=Provider)
def delete_logo_on_provider_delete(sender, instance, **kwargs):
  if instance.logo:
    instance.logo.delete(save=False)


@receiver(post_delete, sender=ServiceImage)
def delete_file_on_serviceimage_delete(sender, instance, **kwargs):
  # Draft-Copies teilen sich die Dateipfade (siehe utils.create_draft_copy),
  # daher Datei nur löschen, wenn kein anderer Eintrag sie noch referenziert.
  if not instance.image:
    return
  name = instance.image.name
  still_referenced = ServiceImage.objects.filter(image=name).exclude(pk=instance.pk).exists()
  if not still_referenced:
    instance.image.delete(save=False)
