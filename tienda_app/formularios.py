from __future__ import annotations

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Order


class FormularioRegistroCliente(UserCreationForm):
    """
    Formulario de registro para clientes finales de la tienda.
    Amplía el formulario base de Django y asegura un email válido.
    """

    email = forms.EmailField(required=True, label="Correo electrónico")
    first_name = forms.CharField(required=False, label="Nombre")
    last_name = forms.CharField(required=False, label="Apellido")

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def save(self, commit: bool = True):
        """
        Guarda al usuario con los datos adicionales capturados.
        """
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data["email"]
        usuario.first_name = self.cleaned_data["first_name"]
        usuario.last_name = self.cleaned_data["last_name"]
        if commit:
            usuario.save()
        return usuario


class FormularioIngreso(AuthenticationForm):
    """
    Formulario de autenticación que permite ingresar con usuario o correo.
    """

    username = forms.CharField(label="Usuario o email")


class FormularioCheckout(forms.ModelForm):
    """
    Formularios para finalizar la compra y confirmar dirección de envío.
    """

    class Meta:
        model = Order
        fields = ("shipping_address", "observations")
        labels = {
            "shipping_address": "Dirección de envío",
            "observations": "Observaciones",
        }
        widgets = {
            "shipping_address": forms.Textarea(attrs={"rows": 3}),
            "observations": forms.Textarea(attrs={"rows": 4}),
        }

