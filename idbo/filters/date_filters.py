from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import AdminDateWidget
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

try:
    import csp
except ImportError:
    csp = None


from collections import OrderedDict

import datetime

import django


class MyDateRangeFilter(BaseRangeFilter):
    _request_key = "DJANGO_RANGEFILTER_ADMIN_JS_LIST"

    def get_timezone(self, _request):
        return timezone.get_default_timezone()

    @staticmethod
    def make_dt_aware(value, tzname):
        if settings.USE_TZ:
            if django.VERSION <= (4, 0, 0) and pytz is not None:
                default_tz = tzname
                if value.tzinfo is not None:
                    value = default_tz.normalize(value)
                else:
                    value = default_tz.localize(value)
            else:
                value = value.replace(tzinfo=tzname)
        return value

    def choices(self, changelist):
        yield {
            # slugify converts any non-unicode characters to empty characters
            # but system_name is required, if title converts to empty string use id
            # https://github.com/silentsokolov/django-admin-rangefilter/issues/18
            "system_name": force_str(
                slugify(self.title) if slugify(self.title) else id(self.title)
            ),
            "query_string": changelist.get_query_string(
                {}, remove=self._get_expected_fields()
            ),
        }

    def _get_expected_fields(self):
        return [self.lookup_kwarg_gte]

    def expected_parameters(self):
        return self._get_expected_fields()

    def _make_query_filter(self, request, validated_data):
        query_params = {}
        date_value_gte = validated_data.get(self.lookup_kwarg_gte, None)

        if date_value_gte:
            data = self.make_dt_aware(
                datetime.datetime.combine(date_value_gte, datetime.time.min),
                self.get_timezone(request),
            )
            if self.field_path == "date":
                query_params["{0}".format(self.field_path)] = data
            else:
                query_params["{0}__date".format(self.field_path)] = data
        return query_params

    def queryset(self, request, queryset):
        if self.form.is_valid():
            validated_data = dict(self.form.cleaned_data.items())
            if validated_data:
                return queryset.filter(
                    **self._make_query_filter(request, validated_data)
                )
        return queryset

    def get_template(self):
        if django.VERSION[:2] <= (1, 8):
            return "rangefilter/date_filter_1_8.html"

        if csp and getattr(settings, "ADMIN_RANGEFILTER_NONCE_ENABLED", True):
            return "rangefilter/date_filter_csp.html"

        return "rangefilter/date_filter.html"

    template = property(get_template)

    def _get_form_fields(self):
        return OrderedDict(
            (
                (
                    self.lookup_kwarg_gte,
                    forms.DateField(
                        label="",
                        widget=AdminDateWidget(attrs={"placeholder": _("Дата")}),
                        localize=True,
                        required=False,
                        initial=self.default_gte,
                    ),
                ),
            )
        )

    def _get_form_class(self):
        fields = self._get_form_fields()

        form_class = type(
            str("DateRangeForm"), (forms.BaseForm,), {"base_fields": fields}
        )

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
