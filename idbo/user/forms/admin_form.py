from django import forms
from user.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _


class AdminAdminForm(forms.ModelForm):
    password = forms.CharField(max_length=88, label="Пароль")

    class Meta:
        model = User

        fields = (
        "profile_image",
        "last_name", "first_name", "middle_name", "login", "password", "email", "is_active", "login")
        
    def clean(self):
        cleaned_data = super().clean()
        try:
            password = cleaned_data['password']
        except:
            raise ValidationError(_('Введите пароль'), code="Поле пароля пустое")
        
        # user = User.objects.get(login=cle)
        
        cleaned_data["password"] = make_password(password)

        cleaned_data["fk_user"] = None

        return cleaned_data

