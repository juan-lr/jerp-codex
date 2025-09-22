from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from mptt.models import MPTTModel, TreeForeignKey

from django.conf import settings
import core.models as core
import resources.models as resources


# ==============================================================================
# Categories
# ==============================================================================

class EquipmentMake(core.DBEnum):
    class Meta:
        verbose_name = 'Equipment Make'
        verbose_name_plural = 'Equipment Makes'
        ordering = ['name']

class EquipmentModel(models.Model):
    class Meta:
        abstract = True
        verbose_name = 'Equipment Model'
        verbose_name_plural = 'Equipment Makes'
        unique_together=[('make', 'name')]

    make = models.ForeignKey(
        EquipmentMake,
        on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)s_related',
        related_query_name='%(app_label)s_%(class)ss',
    )
    name = models.CharField(max_length=settings.DEFAULT_MAX_CHAR)

    cost_dim = models.CharField(
        blank=True,
        null=True,
        choices=core.Dimension,
        default=core.Dimension.TIME
    )
    cost_per_si_unit = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )


    def __str__(self):
        return f'{self.make} - {self.name}'

class TractorModel(EquipmentModel):
    class Meta:
        verbose_name = 'Tractor Model'
        verbose_name_plural = 'Tractor Models'

    horsepower_rated = models.FloatField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(750_000) # 1000 hp ~ 745699.872 watt
        ]
    )

class ImplementHiCat(MPTTModel):
    class Meta:
        verbose_name = 'Implement Category'
        verbose_name_plural = 'Implement Categories'

    name = models.CharField(max_length=settings.DEFAULT_MAX_CHAR)
    parent = TreeForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='children'
    )

    cost_dim = models.CharField(
        blank=True,
        null=True,
        choices=core.Dimension,
        default=core.Dimension.TIME
    )
    cost_per_si_unit = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return self.name

# ==============================================================================
# Instances
# ==============================================================================

class Tractor(resources.AssetABC):
    model = models.ForeignKey(TractorModel, on_delete=models.PROTECT)

    cost_dim = models.CharField(
        blank=True,
        null=True,
        choices=core.Dimension,
        default=core.Dimension.TIME
    )
    cost_per_si_unit = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )

class Implement(resources.AssetABC):
    category = models.ForeignKey(ImplementHiCat, on_delete=models.PROTECT)
    width = models.FloatField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(30) # 35 m ~ 114.8 ft
        ]
    )

    cost_dim = models.CharField(
        blank=True,
        null=True,
        choices=core.Dimension,
        default=core.Dimension.TIME
    )
    cost_per_si_unit = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
