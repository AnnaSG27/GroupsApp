from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "username": "Elige un usuario",
            "email": "tucorreo@ejemplo.com",
            "password1": "••••••••",
            "password2": "••••••••",
        }
        for name in ["username", "email", "password1", "password2"]:
            attrs = self.fields[name].widget.attrs
            attrs.update({
                "class": "form-control input-dark",
                "placeholder": placeholders.get(name, ""),
            })