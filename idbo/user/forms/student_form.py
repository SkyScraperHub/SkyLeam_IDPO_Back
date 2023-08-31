from django import forms
from user.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
import re
class StudentAdminForm(forms.ModelForm):
    password = forms.CharField(min_length=8, max_length=88, label = "Пароль")
    middle_name = forms.CharField( max_length=250, required=False, label = "Отчество")
    class Meta:
        model = User
        fields = ("login", "password",  "last_name", "first_name", "middle_name", "phone_number", "fk_user", "email", "is_active")
        
    def __init__(self, *args, **kwargs):
        super(StudentAdminForm, self).__init__(*args, **kwargs)
        try:
            self.fields["fk_user"].queryset = User.objects.filter(position=User.POSITION_CHOICES[0][0])
        except:
            pass
    def clean(self):
        cleaned_data = super().clean()
        try:
            password = cleaned_data['password']
        except:
            raise ValidationError(_('Введите пароль'), code="Поле пароля пустое")
        self.validate_phone_number(cleaned_data["phone_number"])
        if "middle_name" not in cleaned_data:
            cleaned_data["middle_name"] = "" 
        return cleaned_data
    
    @staticmethod
    def validate_phone_number(value):
      if re.match(r'^\+7[0-9]{10}$', value):
          raise ValidationError(_('Введен неверный номер телефона, приме +79999999999'))
      return value