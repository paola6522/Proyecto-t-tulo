from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Permite autenticación con username O email.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Buscar usuario por username o email
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None
