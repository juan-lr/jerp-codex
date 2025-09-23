from django.contrib.gis.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.gis.db.models.functions import Area

from datetime import date

from django.conf import settings
import organizations.models as orgs
import accounting.models as accounting
import resources.models as resources


# ==============================================================================
# Primatives
# ==============================================================================

class MPolyAreaObject(models.Model):
    class Meta:
        abstract = True

    mpoly = models.MultiPolygonField(
        srid=settings.SRID,
        geography=True,
        blank=True,
        null=True
    )
    area = models.GeneratedField(
        db_persist=True,
        expression=Area('mpoly'),
        output_field=models.FloatField(),
        blank=True,
        null=True
    )

class Site(orgs.OrgObject, MPolyAreaObject):
    class Meta:
        unique_together=[
            ('organization', 'name'),
            ('organization', 'abbreviation')
        ]

    name = models.CharField(max_length=25, unique=True)
    abbreviation = models.CharField(max_length=5, unique=True)
    status = models.CharField(
        max_length=8,
        choices=accounting.AccountingStatus,
        default=accounting.AccountingStatus.RENTED
    )

    def __str__(self):
        return f'{self.name}'


# ==============================================================================
# Other
# ==============================================================================

class Office(Site):
    pass

class Shop(Site):
    pass

# ==============================================================================
# Farming
# ==============================================================================


class Ranch(Site):
    class Meta:
        verbose_name_plural = "Ranches"

class Field(MPolyAreaObject):
    class Meta:
        unique_together = [('ranch', 'name')]
        ordering = ['ranch__name', 'name']

    ranch = models.ForeignKey(Ranch, on_delete=models.PROTECT)
    name = models.CharField(max_length=10)
    accounting_status = models.CharField(
        max_length=8,
        choices=accounting.AccountingStatus,
        default=accounting.AccountingStatus.RENTED
    )

    def __str__(self):
        return f'{self.ranch.abbreviation}_{self.name}'

class FieldState(models.Model):
    class Meta:
        unique_together = [('field', 'date')]
        verbose_name = 'Field State'
        verbose_name_plural = 'Field States'

    field = models.ForeignKey(Field, on_delete=models.PROTECT)
    date = models.DateField(default=date.today)
    soil_quality = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    product = models.ForeignKey(resources.ProductHiCat, on_delete=models.PROTECT)
    plant_date = models.DateField(blank=True, null=True)
