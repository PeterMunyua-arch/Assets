from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AssetAllocation, AssetReturn, Asset

@receiver(post_save, sender=AssetAllocation)
def update_asset_allocation(sender, instance, created, **kwargs):
    if created:  # Only update if a new allocation is created
        instance.asset.is_allocated = True
        instance.asset.is_returned = False
        instance.asset.save()


@receiver(post_save, sender=AssetReturn)
def update_asset_return(sender, instance, created, **kwargs):
    if created:  # Only update if a new return is created
        instance.asset.is_allocated = False
        instance.asset.is_returned = True
        instance.asset.save()