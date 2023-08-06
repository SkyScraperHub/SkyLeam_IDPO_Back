from django import forms
from user.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
#from utils import is_password_hash
def is_password_hash(password):
        if len(password) == 88 and "$" in password:
        # Длина пароля совпадает с длиной хеша пароля и он имеет префикс "pbkdf2_"
        # и имеет разделитель "$" внутри строки, что указывает на то что это salted hash
            return True
        else:
        # Проверяем, является ли строка паролем
            return False
class UserForm(forms.ModelForm):
    password = forms.CharField(max_length=88, label = "Пароль") 
    class Meta:
        model = User

        fields = ( "surname",  "name", "patronymic", "phone_number", "email",
                  "login","password","job_title","admin_type",)
     
    def clean(self):
        cleaned_data = super().clean()
        try:
            password = cleaned_data['password']

        except:
            raise ValidationError(_('Введите пароль'), code="Поле пароля пустое")
        if not is_password_hash(password):
            cleaned_data["password"] = make_password(password)
                
        
        return cleaned_data