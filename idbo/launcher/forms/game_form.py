from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from launcher.models import Game

class GameAdminForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = '__all__'  # или перечислите поля, которые вы хотите включить

    def clean(self):
        cleaned_data = super().clean()
        version = cleaned_data.get("version")
        file = cleaned_data.get("file")

        # Проверить, существует ли объект в базе данных
        if self.instance.pk:
            original_obj = Game.objects.get(id=self.instance.pk)

            # Проверка условий версии и файла
            if original_obj.file != file and original_obj.version.strip() == version.strip():
                # Добавить ошибку к полю 'version'
                self.add_error('version', ValidationError(_('Пожалуйста, обновите версию перед загрузкой обновленного файла.')))
        
        return cleaned_data
