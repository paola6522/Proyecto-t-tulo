# biblioteca/forms_password.py
import re

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm


class CustomPasswordResetForm(PasswordResetForm):
    """
    Formulario personalizado para 'Olvidé mi contraseña'.
    Aquí puedes validar el correo igual que en registro si quieres.
    """

    def clean_email(self):
        email = self.cleaned_data.get("email")

        # Validar formato básico de correo
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValidationError("El correo no tiene un formato válido.")

        # Si quieres, aquí podrías validar que el correo exista en la BD
        # from django.contrib.auth import get_user_model
        # User = get_user_model()
        # if not User.objects.filter(email=email).exists():
        #     raise ValidationError("No existe una cuenta asociada a este correo.")

        return email


class CustomSetPasswordForm(SetPasswordForm):
    """
    Formulario para establecer nueva contraseña (paso después del correo).
    Aquí aplicamos reglas similares a las del registro.
    """

    def clean_new_password1(self):
        password = self.cleaned_data.get("new_password1")

        # Mínimo 8 caracteres
        if len(password or "") < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")

        # Al menos una mayúscula
        if not re.search(r"[A-Z]", password or ""):
            raise ValidationError("La contraseña debe incluir al menos una letra mayúscula.")

        # Al menos un número
        if not re.search(r"[0-9]", password or ""):
            raise ValidationError("La contraseña debe incluir al menos un número.")

        # Al menos un símbolo
        if not re.search(r"[^\w\s]|_", password or ""):
            raise ValidationError("La contraseña debe incluir al menos un símbolo (ej: @, #, !).")

        return password

