from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Facility)
admin.site.register(Sports)
# Inline class for SportField to add it directly inside Turf Admin
class SportFieldInline(admin.TabularInline):
    model = SportField
    extra = 1  # Number of empty forms displayed
    fields = ['field_type', 'sport', 'width', 'height']

# Inline class for SlotEligibility to add it directly inside Turf Admin
class SlotEligibilityInline(admin.TabularInline):
    model = SlotEligibility
    extra = 1
    fields = ['time_slot', 'is_available', 'reason']
    

class PriceEligibilityInline(admin.TabularInline):
    model = Price
    extra = 1
    fields = ['field','time_slot', 'price_per_hour', 'duration_hours','days_of_week']

@admin.register(Turf)
class TurfAdmin(admin.ModelAdmin):
    inlines = [SportFieldInline, SlotEligibilityInline,PriceEligibilityInline]
    list_display = ['name', 'location', 'rating']  
    search_fields = ['name', 'location'] 
admin.site.register(TimeSlot)
admin.site.register(Price)
admin.site.register(SlotEligibility)
admin.site.register(SportField)
