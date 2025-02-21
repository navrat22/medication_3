from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models


class Medication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    dosage = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True, null=True)
    remaining_quantity = models.PositiveIntegerField(default=0)
    last_taken = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return self.name

    def remaining_doses(self):
        return self.remaining_quantity // self.dosage


    def mark_as_taken(self):
        self.remaining_quantity -= 1
        self.last_taken = timezone.now()
        self.save()



class Log(models.Model):
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medication.name}: {self.created_at}"



class Schedule(models.Model):
    DAY_OF_WEEK = [
        ('Monday', 'Pondělí'),
        ('Tuesday', 'Úterý'),
        ('Wednesday', 'Středa'),
        ('Thursday', 'Čtvrtek'),
        ('Friday', 'Pátek'),
        ('Saturday', 'Sobota'),
        ('Sunday', 'Neděle'),
    ]
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)  # Uživatel není povinný
    day_of_week = models.CharField(max_length=9, choices=DAY_OF_WEEK, blank=True, null=True)  # Den může být prázdný
    time = models.TimeField(blank=True, null=True)



    def __str__(self):
        return f"{self.medication.name} - {self.get_day_of_week_display()} v {self.time}"

    def get_day_of_week_display(self):
        return dict(self.DAY_OF_WEEK).get(self.day_of_week, self.day_of_week)



class MedicationStatistics(models.Model):
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_doses_taken = models.PositiveIntegerField(default=0)
    average_doses_per_day = models.FloatField(default=0)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Statistiky pro {self.medication.name} - {self.user.username}"


class MedicationChangeHistory(models.Model):
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    change_date = models.DateTimeField(auto_now_add=True)
    field_changed = models.CharField(max_length=100)
    old_value = models.TextField()
    new_value = models.TextField()
    def __str__(self):
        return f"Změna u {self.medication.name} od {self.user.username} na {self.change_date}"

    
    @classmethod
    def record_change(cls, medication, user, field, old_value, new_value):
        if old_value != new_value:
            cls.objects.create(
                medication=medication,
                user=user,
                field_changed=field,
                old_value=str(old_value),
                new_value=str(new_value))
