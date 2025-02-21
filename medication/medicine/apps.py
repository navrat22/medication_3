from django.apps import AppConfig


class MedicineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'medicine'


class MedicineConfig(AppConfig):
    name = 'medicine'

    def ready(self):
        import medicine.signals