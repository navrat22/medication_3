# Generated by Django 5.1.6 on 2025-02-19 21:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicine', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='day_of_week',
            field=models.CharField(blank=True, choices=[('Monday', 'Pondělí'), ('Tuesday', 'Úterý'), ('Wednesday', 'Středa'), ('Thursday', 'Čtvrtek'), ('Friday', 'Pátek'), ('Saturday', 'Sobota'), ('Sunday', 'Neděle')], max_length=9, null=True),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
