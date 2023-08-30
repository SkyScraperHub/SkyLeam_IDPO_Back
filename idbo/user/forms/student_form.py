from django import forms
from user.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _

class StudentAdminForm(forms.ModelForm):
    password = forms.CharField(max_length=88, label = "Пароль")
    class Meta:
        model = User

        fields = ("login", "password",  "last_name", "first_name", "middle_name", "phone_number", "fk_user", "email", "position", "is_active")
    def __init__(self, *args, **kwargs):
        super(StudentAdminForm, self).__init__(*args, **kwargs)
        self.fields['position'].initial = User.POSITION_CHOICES[1][0]
        self.fields["fk_user"].queryset = User.objects.filter(position=User.POSITION_CHOICES[0][0])

    def clean(self):
        cleaned_data = super().clean()
        try:
            password = cleaned_data['password']
        
        except:
            raise ValidationError(_('Введите пароль'), code="Поле пароля пустое")
        user  = User.objects.get(login = cleaned_data["login"])
        # if user:
            
        cleaned_data["password"] = make_password(password)

        cleaned_data["is_staff"] = True
        
        return cleaned_data