from django import forms
from user.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _


class InstructorAdminForm(forms.ModelForm):
    password = forms.CharField(max_length=88, label="Пароль")

    class Meta:
        model = User

        fields = (
        "last_name", "first_name", "middle_name", "login", "password", "email", "position", "is_active", "login", "password")
    
    def __init__(self, *args, **kwargs):
        super(InstructorAdminForm, self).__init__(*args, **kwargs)
        self.fields['position'].initial = User.POSITION_CHOICES[0][0]
        
    def clean(self):
        cleaned_data = super().clean()
        try:
            password = cleaned_data['password']
        except:
            raise ValidationError(_('Введите пароль'), code="Поле пароля пустое")
        cleaned_data["password"] = make_password(password)
        cleaned_data["fk_user"] = None

        return cleaned_data
