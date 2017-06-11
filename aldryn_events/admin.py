# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from aldryn_apphooks_config.admin import BaseAppHookConfig
from aldryn_reversion.admin import VersionedPlaceholderAdminMixin
from cms.admin.placeholderadmin import PlaceholderAdminMixin
from cms.admin.placeholderadmin import FrontendEditableAdminMixin

try:
    from django_tablib.admin import TablibAdmin
except ImportError:
    TablibAdmin = None

from parler.admin import TranslatableAdmin
from aldryn_translation_tools.admin import AllTranslationsMixin

from .cms_appconfig import EventsConfig
from .models import Event, EventCoordinator, Registration
from .models import RegistrationParticipant
from .forms import EventAdminForm

from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields

class EventAdmin(
    AllTranslationsMixin,
    VersionedPlaceholderAdminMixin,
    FrontendEditableAdminMixin,
    PlaceholderAdminMixin,
    TranslatableAdmin
):
    form = EventAdminForm
    search_fields = ('translations__title', )
    list_display = (
        'title', 'start_date', 'start_time', 'end_date', 'end_time',
        'location', 'is_published', 'app_config',
    )
    list_editable = ('is_published', 'app_config', )
    list_filter = ('is_published', 'app_config', )
    filter_horizontal = ('event_coordinators', )
    date_hierarchy = 'start_date'
    frontend_editable_fields = ('title', 'short_description', 'location')

    _prepopulated_fields = {"slug": ("title",)}

    _fieldsets = (
        (None, {'fields': (
            'title',
            'slug',
            'short_description',
            'image',
            'location',
            ('start_date', 'start_time',),
            ('end_date', 'end_time',),
        )}),
        (_('Advanced'), {
            'classes': ('collapse',),
            'fields': (
                ('location_lat', 'location_lng'),
                'enable_registration',
                'registration_deadline_at',
                'register_link',
                'event_coordinators',
                'detail_link',
                'is_published',
                'publish_at',
                'app_config'
            )
        })
    )

    def get_prepopulated_fields(self, request, obj=None):
        return self._prepopulated_fields

    def get_fieldsets(self, request, obj=None):
        return self._fieldsets


class EventCoordinatorAdmin(VersionedPlaceholderAdminMixin, admin.ModelAdmin):
    list_display = ['full_name', 'email_address']


class RegistrationAdmin(TablibAdmin if TablibAdmin is not None
                        else admin.ModelAdmin):
    # html is giving me Unicode Error when using accentuated characters,
    # related issue create on django-tablib:
    # https://github.com/joshourisman/django-tablib/issues/43
    formats = ['xls', 'csv', 'html']
    list_display = ('email', 'first_name', 'last_name', 'event')
    list_filter = ('event', )
    date_hierarchy = 'created_at'

class EventTitleResourceField(fields.Field):
    def get_value(self, obj):
        return obj.registration.event
class RegistrationTitleResourceField(fields.Field):
    def get_value(self, obj):
        return obj.registration

class RegistrationParticipantResource(resources.ModelResource):
    event_title = EventTitleResourceField(column_name='event_title')
    registration_title = RegistrationTitleResourceField(column_name='registration_title')
    class Meta:
        model = RegistrationParticipant
        fields = (
            'first_name',
            'last_name',
            'registration__salutation',
            'registration__first_name',
            'registration__last_name',
            'registration__first_name',
            'registration__address',
            'registration__address_zip',
            'registration__address_city',
            'registration__phone',
            'registration__mobile',
            'registration__email',
            'registration__message',
            'registration__created_at',
            'registration__modified_at',
            'event_title',
            'registration_title',
        )

class RegistrationParticipantAdmin(ImportExportModelAdmin):
    resource_class = RegistrationParticipantResource
    list_display = ('first_name', 'last_name', 'registration', 'event',)
    list_filter = ('registration__event', )
    search_fields = ['first_name', 'last_name', 'registration__email', 'registration__first_name', 'registration__last_name',]
    date_hierarchy = 'created_at'
    def event(self, instance):
        return instance.registration.event
    def get_queryset(self, request):
        qry = super(RegistrationParticipantAdmin, self).get_queryset(request).select_related('registration', 'registration__event',)
        return qry

class EventConfigAdmin(VersionedPlaceholderAdminMixin,
                       AllTranslationsMixin,
                       BaseAppHookConfig,
                       TranslatableAdmin):
    def get_config_fields(self):
        return ('app_title', 'latest_first', 'config.show_ongoing_first', )


admin.site.register(Event, EventAdmin)
admin.site.register(EventCoordinator, EventCoordinatorAdmin)
admin.site.register(Registration, RegistrationAdmin)
admin.site.register(RegistrationParticipant, RegistrationParticipantAdmin)
admin.site.register(EventsConfig, EventConfigAdmin)
