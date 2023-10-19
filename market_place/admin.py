from django.contrib import admin

from booking.models import Booking
from .models import StorageBox

from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from django import forms
from django.contrib.admin import DateFieldListFilter

from django.contrib.admin.filters import DateFieldListFilter
from django.db.models import Q

class DateRangeAvailabilityFilter(DateFieldListFilter):
    def __init__(self, *args, **kwargs):
        super(DateRangeAvailabilityFilter, self).__init__(*args, **kwargs)

    def queryset(self, request, queryset):
        if self.used_parameters.get('start_date__gte', None) and self.used_parameters.get('end_date__lte', None):
            start_date = self.used_parameters['start_date__gte']
            end_date = self.used_parameters['end_date__lte']

            # Filter StorageBox objects that have bookings within the date range
            booked_boxes = Booking.objects.filter(
                Q(start_date__lte=end_date) & Q(end_date__gte=start_date)
            ).values_list('storage_box', flat=True)

            # Exclude booked boxes from the queryset
            return queryset.exclude(id__in=booked_boxes)

        return super(DateRangeAvailabilityFilter, self).queryset(request, queryset)


class AvailabilityListFilter(SimpleListFilter):
    title = _('availability')  # Human-readable title
    parameter_name = 'availability'  # URL query parameter

    def lookups(self, request, model_admin):
        # This method returns a list of tuples. The first value in each tuple is the coded value for the option that will appear in the URL query. The second value is the human-readable name for the option that will appear in the right sidebar.
        return (
            ('available', _('Available')),
            ('booked', _('Booked')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'available':
            # Get all StorageBox IDs that have bookings
            booked_boxes = Booking.objects.values_list('storage_box', flat=True)
            return queryset.exclude(id__in=booked_boxes)

        elif self.value() == 'booked':
            booked_boxes = Booking.objects.values_list('storage_box', flat=True)
            return queryset.filter(id__in=booked_boxes)


# Update the StorageBoxAdmin class:

@admin.register(StorageBox)
class StorageBoxAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'surface', 'display_monthly_price', 'display_owner')
    ordering = ('-id',)
    list_filter = (
        'surface',
        AvailabilityListFilter,
        ('booking__start_date', DateRangeAvailabilityFilter),
        ('booking__end_date', DateRangeAvailabilityFilter)
    )

    def display_monthly_price(self, obj):
        return f"{obj.monthly_price.initial[0]} {obj.monthly_price.initial[1]}"

    display_monthly_price.short_description = "Monthly Price"

    def display_owner(self, obj):
        return f"{obj.owner.first_name} {obj.owner.last_name}"

    display_owner.short_description = "Owner"
