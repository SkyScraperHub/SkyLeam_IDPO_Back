from django import forms
from user.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _

class StudentAdminForm(forms.ModelForm):
    password = forms.CharField(max_length=88, label = "Пароль") 
    class Meta:
        model = User

        fields = ("login", "password",  "last_name", "first_name", "middle_name", "phone_number", "fk_user", "email", "position", "is_active", "is_staff")
     
    def clean(self):
        cleaned_data = super().clean()
        try:
            password = cleaned_data['password']
        
        except:
            raise ValidationError(_('Введите пароль'), code="Поле пароля пустое")
        cleaned_data["password"] = make_password(password)
                
        
        return cleaned_data