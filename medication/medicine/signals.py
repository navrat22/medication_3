# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Medication, MedicationStatistics
from django.utils import timezone

@receiver(post_save, sender=Medication)
def update_medication_statistics(sender, instance, created, **kwargs):

    stats, created = MedicationStatistics.objects.get_or_create(
        user=instance.user,
        medication=instance
    )

    stats.total_doses_taken += 1


    if instance.last_taken:
        days_since_last_use = (timezone.now() - instance.last_taken).days or 1
        stats.average_doses_per_day = stats.total_doses_taken / days_since_last_use
    else:
        stats.average_doses_per_day = 0

    stats.save()
