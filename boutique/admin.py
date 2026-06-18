from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'phone',
        'email',
        'service',
        'appointment_date',
        'appointment_time',
        'created_at'
    )

    search_fields = ('name', 'phone', 'email')
    list_filter = ('service', 'appointment_date')


from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ('name', 'rating', 'is_approved', 'created_at')
    list_filter   = ('is_approved',)
    list_editable = ('is_approved',)
    ordering      = ('-created_at',)    