# biblioteca/forms_password.py

import re

from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm


class CustomPasswordResetForm(PasswordResetForm):
    """
    Formulario personalizado para 'Olvidé mi contraseña'.
    Valida que el correo tenga formato correcto.
    """

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if not email:
            raise ValidationError("Debes ingresar un correo electrónico.")

        # Validar formato básico de correo
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValidationError("El correo no tiene un formato válido.")

        # Si quieres validar que exista en la BD, descomenta esto:
        # from django.contrib.auth import get_user_model
        # User = get_user_model()
        # if not User.objects.filter(email=email).exists():
        #     raise ValidationError("No existe una cuenta asociada a este correo.")

        return email


class CustomSetPasswordForm(SetPasswordForm):
    """
    Formulario para establecer nueva contraseña (después del correo),
    con las MISMAS validaciones que tu registro.
    """

    def clean_new_password1(self):
        password = self.cleaned_data.get("new_password1") or ""

        # 1. Contraseñas comunes
        comunes = ["123456", "password", "qwerty", "admin"]
        if password.lower() in comunes:
            raise ValidationError("La contraseña es demasiado común.")

        # 2. Largo mínimo
        if len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")

        # 3. Mayúscula
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Debe contener al menos una letra mayúscula.")

        # 4. Minúscula
        if not re.search(r"[a-z]", password):
            raise ValidationError("Debe contener al menos una letra minúscula.")

        # 5. Número
        if not re.search(r"\d", password):
            raise ValidationError("Debe contener al menos un número.")

        # 6. Carácter especial
        if not re.search(r"[^\w\s]|_", password):
            raise ValidationError(
                "Debe contener al menos un carácter especial (ej. !, @, #, $, %, &, *, ?, _, -)."
            )

        # 7. No permitir más de 3 repetidos seguidos
        if re.search(r"(.)\1\1", password):
            raise ValidationError("No puede contener más de 3 caracteres iguales seguidos.")

        return password
