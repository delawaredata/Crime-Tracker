from myproject.crime.models import Incident, Victim, Suspect
from django.contrib import admin


class IncidentAdmin(admin.ModelAdmin):
    list_display = ('headline', 'inc_date', 'is_homicide', 'victim_count', 'killed_count', 'is_suspects_unknown')
    list_editable = ('victim_count', 'killed_count')
    list_filter = ['inc_date', 'is_homicide', 'is_suspects_unknown', 'is_victims_unknown', 'victim_count', 'killed_count']
    search_fields = ['headline']
    ordering = ['-inc_date']
    prepopulated_fields = {"inc_slug": ("headline",)}
    raw_id_fields = ("victims", "suspects",)
    fieldsets = [
        ('Details', {'fields':['headline', ('inc_date', 'inc_time'), ('inc_type', 'is_homicide'), 'summary']}),
        ('Location', {'fields':['is_approximate_address', 'address', 'city', 'state']}),
        ('Victim Info.', {'fields':[('victim_count', 'killed_count'), 'is_victims_unknown', 'victims']}),
        ('Suspect Info.', {'fields':['suspect_count', 'is_suspects_unknown', 'suspects']}),
        ('DO NOT TOUCH', {'fields':[('latitude', 'longitude'), 'formatted_address', 'inc_slug']}),
    ]
    actions = ['mark_as_homicide']

    def mark_as_homicide(self, request, queryset):
        queryset.update(is_homicide=True)
    mark_as_homicide.short_description = "Mark incidents as homicides"


class VictimAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'age', 'sex', 'is_unidentified', 'is_killed')
    list_editable = ('age', 'is_killed')
    list_filter = ['sex', 'is_killed', 'is_unidentified']
    search_fields = ['last_name', 'first_name']
    prepopulated_fields = {'vic_slug': ('last_name', 'first_name')}
    fieldsets = [
        ('Bio.', {'fields':['is_unidentified', ('first_name', 'last_name'), ('age', 'sex')]}),
        ('Incident Info.', {'fields':['is_killed', 'about']}),
        ('Misc.', {'fields':['victim_photo', 'cropping', 'vic_slug']}),
    ]


class SuspectAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'age', 'sex', 'is_unidentified', 'arrest_date')
    list_editable = ('age', 'arrest_date')
    list_filter = ['arrest_date', 'sex', 'is_unidentified']
    search_fields = ['last_name', 'first_name']
    prepopulated_fields = {'suspect_slug': ('last_name', 'first_name')}
    fieldsets = [
        ('Bio.', {'fields':['is_unidentified', ('first_name', 'last_name'), ('age', 'sex')]}),
        ('Incident Info.', {'fields':['arrest_date', 'about']}),
        ('Misc.', {'fields':['suspect_photo', 'cropping', 'suspect_slug']})
    ]

admin.site.register(Incident, IncidentAdmin)
admin.site.register(Victim, VictimAdmin)
admin.site.register(Suspect, SuspectAdmin)
