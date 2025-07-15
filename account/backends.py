from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()

class PhoneEmailAuthBackend(ModelBackend):
    """Authentication using either email or phone instead of username."""
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        try:
            user = User.objects.get(Q(phone=username) | Q(email=username))
        except User.DoesNotExist:
            return None
        
        if user.check_password(password):
            return user
        return None
