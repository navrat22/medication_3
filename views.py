from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import MedicationForm, ScheduleForm, MedicationCreateForm
from .models import Medication, MedicationStatistics, Schedule, Drug, MedicationChangeHistory


class MedicineListView(LoginRequiredMixin, ListView):
    model = Medication
    template_name = 'medication_list.html'
    context_object_name = 'medications'

    def get_queryset(self):
        return  Medication.objects.filter(user=self.request.user)



class MedicationCreateView(LoginRequiredMixin, CreateView):
    model = Medication
    form_class = MedicationForm
    template_name = 'medication_form.html'
    success_url = reverse_lazy('medication_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)


        day_of_week = form.cleaned_data.get('day_of_week')
        time = form.cleaned_data.get('time')

        if day_of_week and time:
            Schedule.objects.create(
                medication=self.object,
                user=self.request.user,
                day_of_week=day_of_week,
                time=time
            )

        return response



class MedicationUpdateView(LoginRequiredMixin, UpdateView):
    model = Medication
    form_class = MedicationForm
    template_name = 'medication_form.html'
    success_url = reverse_lazy('medication_list')

    def get_queryset(self):

        return Medication.objects.filter(user=self.request.user)

    def form_valid(self, form):
        old_dosage = self.object.dosage
        old_notes = self.object.notes
        old_remaining_quantity = self.object.remaining_quantity
        response = super().form_valid(form)

        if old_dosage != self.object.dosage:
            MedicationChangeHistory.objects.create(
                medication=self.object,
                change_date=timezone.now(),
            )
        if old_notes != self.object.notes:
            MedicationChangeHistory.objects.create(
                medication=self.object,
                change_date=timezone.now(),
            )
        if old_remaining_quantity != self.object.remaining_quantity:
            MedicationChangeHistory.objects.create(
                medication=self.object,
                change_date=timezone.now(),
            )

        return response

class MedicationDeleteView(LoginRequiredMixin, DeleteView):
    model = Medication
    template_name = 'medication_delete.html'
    success_url = reverse_lazy('medication_list')

    def get_queryset(self):
        return Medication.objects.filter(user=self.request.user)



@login_required
def mark_as_taken(request, med_id):
    medication = get_object_or_404(Medication, id=med_id)

    if medication.remaining_quantity > 0:
        medication.mark_as_taken()

        MedicationChangeHistory.objects.create(
            medication=medication,
            change_date=timezone.now(),
        )

    return redirect('medication_list')


@login_required
def add_medication(request):
    if request.method == 'POST':
        form = MedicationCreateForm(request.POST)

        if form.is_valid():
            medication = form.save(commit=False)
            medication.user = request.user  # Přidání uživatele k léku
            medication.save()


            return redirect('medication_list')  # Přesměrování zpět na seznam léků
    else:
        form = MedicationCreateForm()

    return render(request, 'medication_form.html', {'form': form})


@login_required
def medication_statistics(request):
    stats = MedicationStatistics.objects.filter(user=request.user)
    return render(request, 'statistics.html', {'stats': stats})




@login_required
def update_medication(request, med_id):
    medication = get_object_or_404(Medication, id=med_id)

    if request.method == 'POST':
        form = MedicationForm(request.POST, instance=medication)
        if form.is_valid():
            old_dosage = medication.dosage
            old_notes = medication.notes
            old_remaining_quantity = medication.remaining_quantity

            medication = form.save()


            if old_dosage != medication.dosage:
                MedicationChangeHistory.objects.create(
                    medication=medication,
                    change_date=timezone.now(),
                )
            if old_notes != medication.notes:
                MedicationChangeHistory.objects.create(
                    medication=medication,
                    change_date=timezone.now(),
                )
            if old_remaining_quantity != medication.remaining_quantity:
                MedicationChangeHistory.objects.create(
                    medication=medication,
                    change_date=timezone.now(),
                )

            return redirect('medication_list')
    else:
        form = MedicationForm(instance=medication)

    return render(request, 'medication_form.html', {'form': form})


@login_required
def medication_history(request, med_id):
    medication = get_object_or_404(Medication, id=med_id)
    changes = MedicationChangeHistory.objects.filter(medication=medication).order_by('-change_date')
    return render(request, 'medication_change_history.html', {
        'medication': medication,
        'changes': changes
    })
