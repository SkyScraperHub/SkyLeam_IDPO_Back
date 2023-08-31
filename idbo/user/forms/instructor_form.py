from django import forms
from user.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
import re

class InstructorAdminForm(forms.ModelForm):
    middle_name = forms.CharField( max_length=250, required=False, label = "Отчество")
    
    class Meta:
        model = User

        fields = ("last_name", "first_name", "middle_name", "login", "password", "phone_number", "email", "is_active")
        
    def clean(self):
        cleaned_data = super().clean()
        try:
            password = cleaned_data['password']
        except:
            raise ValidationError(_('Введите пароль'), code="Поле пароля пустое")
        self.validate_phone_number(cleaned_data["phone_number"])
        if len(password) < 8:
            raise ValidationError(_('Минимальная длина пароля 8 символов'), code="Пароль слишком маленький")
        return cleaned_data
    
    @staticmethod
    def validate_phone_number(value):
        if re.match(r'^\+7[0-9]{10}$', value) is None:
            raise ValidationError(_('Введен неверный номер телефона, пример +79999999999'), params={"phone_number":"ERROR"})
        return value
