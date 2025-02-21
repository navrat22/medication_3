from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView





class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()  # Uložení uživatele
        login(self.request, user)  # Automatické přihlášení uživatele
        return redirect(self.success_url)  # Přesměrování na stránku přihlášení (nebo jinou)

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_object(self):
        return self.request.user

