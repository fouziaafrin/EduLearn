from django.core.exceptions import ValidationError

class NoReuseOldPasswordValidator:
    def validate(self, password, user=None):
        if user and user.check_password(password):
            raise ValidationError("New password cannot be the same as the old password.")

    def get_help_text(self):
        return "Your new password cannot be the same as your old password."
