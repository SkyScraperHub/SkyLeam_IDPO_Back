from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import AdminIntegerFieldWidget, AdminDateWidget
from django.contrib.admin.widgets import AdminSplitDateTime as BaseAdminSplitDateTime
from django.template.defaultfilters import slugify
from django.templatetags.static import StaticNode
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.html import format_html
from rangefilter.filters import BaseRangeFilter, OnceCallMedia
from django.utils.translation import gettext_lazy as _
try:
    import pytz
except ImportError:
    pytz = None


from collections import OrderedDict

import datetime

import django


class IdFilter(BaseRangeFilter):
    _request_key = "DJANGO_RANGEFILTER_ADMIN_JS_LIST"

    def choices(self, changelist):
        yield {
            # slugify converts any non-unicode characters to empty characters
            # but system_name is required, if title converts to empty string use id
            # https://github.com/silentsokolov/django-admin-rangefilter/issues/18
            "system_name": force_str(
                slugify(self.title) if slugify(self.title) else id(self.title)
            ),
            "query_string": changelist.get_query_string({}, remove=self._get_expected_fields()),
        }

    def _get_expected_fields(self):
        return [self.lookup_kwarg_gte]

    def expected_parameters(self):
        return self._get_expected_fields()

    def _make_query_filter(self, request, validated_data):
        query_params = {}
        date_value_gte = validated_data.get(self.lookup_kwarg_gte, None)

        return query_params

    def queryset(self, request, queryset):
        if self.form.is_valid():
            validated_data = dict(self.form.cleaned_data.items())
            if validated_data:
                return queryset.filter(id=validated_data["id__range__gte"])
        return queryset

    def get_template(self):

        return "rangefilter/numeric_filter.html"

    template = property(get_template)

    def _get_form_fields(self):
        return OrderedDict(
            (
                (
                    self.lookup_kwarg_gte,
                    forms.IntegerField(
                        label="",
                        widget=AdminIntegerFieldWidget(
                            attrs={"placeholder": _("ID")}),
                        localize=True,
                        required=False,
                        initial=self.default_gte,
                    ),
                ),
            )
        )

    def _get_form_class(self):
        fields = self._get_form_fields()

        form_class = type(str("DateRangeForm"), (forms.BaseForm,), {
                          "base_fields": fields})
        if self.title == "id":
            self.title = "ID пользователя"
        # lines below ensure that the js static files are loaded just once
        # even if there is more than one DateRangeFilter in use
        js_list = getattr(self.request, self._request_key, None)
        if not js_list:
            js_list = OnceCallMedia()
            setattr(self.request, self._request_key, js_list)

        form_class.js = js_list

        return form_class

    def get_form(self, _request):
        form_class = self._get_form_class()
        return form_class(self.used_parameters or None)
