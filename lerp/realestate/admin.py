from django.contrib.gis import admin
from leaflet.admin import LeafletGeoAdmin

from .models import (
    Ranch,
    Field,
    FieldState,
)

# ==============================================================================
# Real-Estate
# ==============================================================================

@admin.register(FieldState) # consider adding inline in field
class FieldStateAdmin(admin.ModelAdmin):
    search_fields = ['field', 'date']

@admin.register(Field)
class FieldAdmin(LeafletGeoAdmin):
    list_display = ['ranch__name', 'name', 'area', 'ranch__organization__name']
    search_fields = ['ranch__name', 'name', 'ranch__organization__name']
    list_filter = ['ranch__organization__name', 'ranch__name']

class FieldInLine(admin.TabularInline):
    model = Field
    extra = 3

@admin.register(Ranch)
class RanchAdmin(LeafletGeoAdmin):
    """
    fieldsets = [
        (None, {'fields': ['name', 'abbreviation']}),
        ('ORGANIZATION', {'fields': ['organization', 'status']})
    ]
    """

    #inlines = [FieldInLine]
    list_display = ['name', 'abbreviation', 'organization'] # 'field_count', 'total_area'] etc.
    list_filter = ['organization']
    search_fields = ['name'] # TODO this (& filter?) not working with foreignkey (e.g. organization)
