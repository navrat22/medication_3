from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models


class Drug(models.Model):#,pocet tablet#
    """
        Model representing a drug and its quantity details.

        Attributes:
            created_at (DateTimeField): The timestamp when the drug entry was created.
            quantity (PositiveIntegerField): The quantity of the drug in the specified unit.
            unit (CharField): The unit of the drug's quantity, either 'mg' (milligrams) or 'g' (grams).
                               Defaults to 'mg' if not specified.

        Methods:
            __str__ (str): Returns a string representation of the drug, showing the quantity, unit, and creation timestamp.
        """
    created_at = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField(default=1)
    unit = models.CharField(max_length=10,choices=[('mg', 'mg'), ('g', 'g')],default='mg')

    def __str__(self):
        return f"{self.quantity} {self.unit} - Přidáno: {self.created_at}"


class Medication(models.Model):
    """
        Model representing a medication prescribed to a user, including dosage, remaining quantity, and tracking when it was last taken.

        Attributes:
            user (ForeignKey): The user to whom the medication is prescribed.
            name (CharField): The name of the medication.
            dosage (PositiveIntegerField): The dosage of the medication (e.g., how many milligrams or tablets per dose).
            notes (TextField): Optional notes related to the medication. Can be left blank.
            remaining_quantity (PositiveIntegerField): The quantity of medication remaining (how many doses left).
            last_taken (DateTimeField): The timestamp of when the medication was last taken by the user. Can be null if not yet taken.
            drug (ForeignKey): The related drug that this medication refers to. References the **Drug** model.
            schedules (ManyToManyField): The related schedules related to this medication.

        Methods:
            __str__ (str): Returns the name of the medication as a string representation.
            remaining_doses (int): Calculates the number of remaining doses based on the quantity and dosage.
            mark_as_taken (None): Marks the medication as taken by reducing the remaining quantity by one and updating the timestamp of when it was last taken.
        """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    dosage = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True, null=True)
    remaining_quantity = models.PositiveIntegerField(default=0)
    last_taken = models.DateTimeField(blank=True, null=True)
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name="medications", null=True)
    schedules = models.ManyToManyField('Schedule', related_name='medications')

    def __str__(self):
        return self.name

    def remaining_doses(self):#zbyv.davky#
        return self.remaining_quantity // self.dosage


    def mark_as_taken(self): #uzil davku #
        self.remaining_quantity -= 1
        self.last_taken = timezone.now()
        self.save()



class Schedule(models.Model):
    """
       Model representing a schedule for medication intake, specifying the day of the week and time when a medication should be taken.

       Attributes:
           DAY_OF_WEEK (list of tuples): A list of days of the week (in English) mapped to their Czech translations.
           day_of_week (CharField): The day of the week when the medication is to be taken. This field uses the choices defined in `DAY_OF_WEEK`.
           time (TimeField): The time at which the medication is to be taken. This field can be left blank if no time is set.

       Methods:
           __str__ (str): Returns a string representation of the schedule, showing the day and time.
           get_day_of_week_display (str): Returns the Czech name of the day of the week, based on the stored value.
       """
    DAY_OF_WEEK = [
        ('Monday', 'Pondělí'),
        ('Tuesday', 'Úterý'),
        ('Wednesday', 'Středa'),
        ('Thursday', 'Čtvrtek'),
        ('Friday', 'Pátek'),
        ('Saturday', 'Sobota'),
        ('Sunday', 'Neděle'),
    ]
    day_of_week = models.CharField(max_length=9, choices=DAY_OF_WEEK, blank=True, null=True)
    time = models.TimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_day_of_week_display()} v {self.time}"

    def get_day_of_week_display(self):
        return dict(self.DAY_OF_WEEK).get(self.day_of_week, self.day_of_week)



class MedicationStatistics(models.Model):
    """
        Model representing statistics for a specific medication, including the average doses taken per day and the date of the last update.

        Attributes:
            medication (ForeignKey): The medication for which the statistics are being tracked. It is related to the **Medication** model.
            user (ForeignKey): The user for whom the medication statistics are recorded. It is related to the **User** model.
            average_doses_per_day (FloatField): The average number of doses taken per day for the medication by the user. This value is used to track the user's usage pattern.
            last_update (DateTimeField): The timestamp of the last time the statistics were updated.
            total_doses_taken (PositiveIntegerField)

        Methods:
            __str__ (str): Returns a string representation of the statistics, showing the medication name and the username of the user.
        """
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    average_doses_per_day = models.FloatField(default=0) #prum.pocet davek#
    last_update = models.DateTimeField(auto_now=True)
    total_doses_taken = models.PositiveIntegerField(default=0)#zvysuje se pokazde kdy se uzije lek, sleduje se celkovy pocet davek#

    def __str__(self):
        return f"Statistiky pro {self.medication.name} - {self.user.username}"



class Comment(models.Model):
    """
        Model representing a comment on a specific medication.

        Attributes:
            medication (OneToOneField): A one-to-one relationship to the **Medication** model, indicating which medication the comment is associated with.
            content (TextField): The content of the comment, where users can write their feedback or notes about the medication.
            created_at (DateTimeField): The timestamp of when the comment was created. This field is automatically set when the comment is added.

        Methods:
            __str__ (str): Returns a string representation of the comment, showing the medication name and the timestamp when the comment was created.
        """
    medication = models.OneToOneField(Medication, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Komentář pro {self.medication.name} - {self.created_at}"



class MedicationChangeHistory(models.Model):
    """
        Model representing the history of changes made to a specific medication.

        Attributes:
            medication (ForeignKey): A foreign key linking the change history to the specific **Medication** model, representing the medication whose change history is recorded.
            change_date (DateTimeField): A field automatically set to the date and time when the change was made. It tracks when the change was logged.

        Methods:
            __str__ (str): Returns a string representation of the change history entry, displaying the medication's name and the date of the change.
        """
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    change_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Změna u {self.medication.name}  na {self.change_date}"


