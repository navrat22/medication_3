from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import MedicationForm, ScheduleForm
from .models import Medication, MedicationStatistics, Schedule, Log, MedicationChangeHistory


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

        # Logování užité dávky
        Log.objects.create(medication=medication)

    return redirect('medication_list')


@login_required
def add_dose(request, med_id):
    medication = get_object_or_404(Medication, id=med_id, user=request.user)

    if request.method == "POST":
        action = request.POST.get('action')

        if action == 'increase':
            medication.remaining_quantity += 1
        elif action == 'decrease' and medication.remaining_quantity > 0:
            medication.remaining_quantity -= 1

        medication.save()

    return redirect('medication_list')




@login_required
def medication_statistics(request):

    stats = MedicationStatistics.objects.filter(user=request.user)


    return render(request, 'statistics.html', {'stats': stats})


@login_required
def add_medication(request):
    if request.method == 'POST':
        medication_form = MedicationForm(request.POST)
        schedule_form = ScheduleForm(request.POST)

        if medication_form.is_valid():
            medication = medication_form.save(commit=False)
            medication.user = request.user
            medication.save()


            if schedule_form.is_valid() and schedule_form.cleaned_data['day_of_week'] and schedule_form.cleaned_data['time']:
                schedule = schedule_form.save(commit=False)
                schedule.medication = medication
                schedule.user = request.user
                schedule.save()

            return redirect('medication_list')

    else:
        medication_form = MedicationForm()
        schedule_form = ScheduleForm()

    return render(request, 'medication_form.html', {
        'medication_form': medication_form,
        'schedule_form': schedule_form
    })


@login_required
def update_medication(request, med_id):
    medication = get_object_or_404(Medication, id=med_id)

    if request.method == 'POST':
        form = MedicationForm(request.POST, instance=medication)
        if form.is_valid():
            # Uložení starých hodnot pro porovnání
            old_dosage = medication.dosage
            old_notes = medication.notes
            old_remaining_quantity = medication.remaining_quantity


            medication = form.save()

            # Záznam změn
            if old_dosage != medication.dosage:
                MedicationChangeHistory.record_change(medication, request.user, "dosage", old_dosage, medication.dosage)
            if old_notes != medication.notes:
                MedicationChangeHistory.record_change(medication, request.user, "notes", old_notes, medication.notes)
            if old_remaining_quantity != medication.remaining_quantity:
                MedicationChangeHistory.record_change(medication, request.user, "remaining_quantity", old_remaining_quantity, medication.remaining_quantity)

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
