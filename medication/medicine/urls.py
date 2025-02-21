from django.urls import path


from.views import MedicineListView, MedicationCreateView, MedicationUpdateView, \
    MedicationDeleteView, mark_as_taken
from .import views

urlpatterns = [
    path('', MedicineListView.as_view(), name='medication_list'),
    path('add/', MedicationCreateView.as_view(), name='medication_add'),
    path('update/<int:pk>/', MedicationUpdateView.as_view(), name='medication_update'),
    path('delete/<int:pk>/', MedicationDeleteView.as_view(), name='medication_delete'),
    path('medication/<int:med_id>/mark_as_taken/',views.mark_as_taken, name='mark_as_taken'),
    path('medication/<int:med_id>/add_dose/', views.add_dose, name='add_dose'),
    path('statistics/', views.medication_statistics, name='statistics'),
    path('medication/<int:med_id>/history/', views.medication_history, name='medication_history'),

]