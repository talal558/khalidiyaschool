from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        email = kwargs.get("email") or username
        if not email:
            return None

        # Single-query path — eliminates timing difference between
        # "user exists" and "user not found" that would allow email enumeration.
        user = UserModel.objects.filter(email__iexact=email).order_by("id").first()

        if user is None:
            # Run a dummy check_password so response time stays constant
            # regardless of whether the email exists in the database.
            UserModel().check_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
