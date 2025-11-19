from django.contrib import admin
from biblioteca.models import Libro, Categoria, LibroLeido, DiarioLector
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.core.mail import send_mail
from django.conf import settings

# -----------------------
# Registrar tus modelos
# -----------------------
admin.site.register(Categoria)
admin.site.register(Libro)
admin.site.register(LibroLeido)
admin.site.register(DiarioLector)

# -----------------------
# Acción para eliminar usuarios e informar por correo
# -----------------------
def eliminar_usuarios_y_enviar_correo(modeladmin, request, queryset):
    """
    Acción de admin:
    - Envía un correo a cada usuario seleccionado
    - Luego elimina la cuenta
    """
    for user in queryset:
        email = user.email  # Guardamos el correo ANTES de borrar

        if email:
            asunto = "Tu cuenta ha sido eliminada de Mi Rincón de Letras y Té"
            mensaje = (
                f"Hola {user.username},\n\n"
                "Hemos detectado que tu cuenta ha estado inactiva durante un periodo prolongado, "
                "por lo que ha sido eliminada de manera automática.\n\n"
                "Si deseas volver a usar la aplicación, puedes registrarte nuevamente cuando quieras. 🧁📚\n\n"
                "Un abrazo lector,\n"
                "Mi Rincón de Letras y Té"
            )

            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,  # Remitente
                [email],
                fail_silently=True,  # Para que no reviente si hay error de correo
            )

        # Finalmente, eliminamos el usuario
        user.delete()

eliminar_usuarios_y_enviar_correo.short_description = (
    "Eliminar usuarios seleccionados y enviar correo de aviso"
)

# -----------------------
# Personalizar cómo se ve User en el admin
# -----------------------
class CustomUserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "date_joined", "last_login", "is_active")
    list_filter = ("is_active", "date_joined", "last_login")
    search_fields = ("username", "email")
    actions = [eliminar_usuarios_y_enviar_correo]

# Primero desregistramos el User que ya viene registrado por Django
admin.site.unregister(User)

# Luego registramos nuestra versión personalizada
admin.site.register(User, CustomUserAdmin)

