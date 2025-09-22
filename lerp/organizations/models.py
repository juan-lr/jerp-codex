from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from taggit.managers import TaggableManager
from simple_history.models import HistoricalRecords

from django.conf import settings
import core.models as core
import organizations.models as orgs
import accounting.models as accounting


# ==============================================================================
# Categories
# ==============================================================================

class ActivityHiCat(orgs.HierarchicalOrgCode):
    class Meta:
        verbose_name = 'Activity Category'
        verbose_name_plural = 'Activity Categories'

    rate_numerator_dimension = models.CharField(
        help_text='Usually area or length (distance)',
        max_length=13,
        choices=core.Dimension.choices,
        default=core.Dimension.AREA,
        blank=True,
        null=True
    )
    rate_denominator_dimension = models.CharField(
        help_text='Usually time or quantity',
        max_length=13,
        choices=core.Dimension.choices,
        default=core.Dimension.TIME,
        blank=True,
        null=True
    )
    rate_benchmark = models.FloatField(blank=True, null=True)

    """
    '''
    Costs to default back to if activity element costs invalid.
    Element costs should be prioritized in both reporting AND INPUT.
    '''
    default_cost_dim = models.CharField(
        blank=True,
        null=True,
        choices=core.Dimension,
        default=core.Dimension.TIME
    )
    default_cost_per_si_unit = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    """

class LaborHiCat(orgs.HierarchicalOrgCode):
    class Meta:
        verbose_name = 'Labor Category'
        verbose_name_plural = 'Labor Categories'

    cost_dim = models.CharField(
        blank=True,
        null=True,
        choices=core.Dimension,
        default=core.Dimension.TIME,
        verbose_name='Cost measured by',
    )
    cost_per_si_unit = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name='Cost per SI unit',
    )

class MaterialHiCat(orgs.HierarchicalOrgCode):
    class Meta:
        verbose_name = 'Material Category'
        verbose_name_plural = 'Material Categories'

    cost_dim = models.CharField(
        blank=True,
        null=True,
        choices=core.Dimension,
        verbose_name='Cost measured by',
    )
    cost_per_si_unit = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name='Cost per SI unit',
    )

class ProductHiCat(orgs.HierarchicalOrgCode):
    class Meta:
        verbose_name = 'Product Category'
        verbose_name_plural = 'Product Categories'

    price_dim = models.CharField(
        blank=True,
        null=True,
        choices=core.Dimension,
        default=core.Dimension.MASS,
        verbose_name='Price measured by',
    )
    price_per_si_unit = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name='Price per SI unit',
    )

# ==============================================================================
# Instances
# ==============================================================================

class AssetABC(orgs.OrgObject):
    class Meta:
        abstract = True
        unique_together=[('organization', 'asset_id')]
        ordering = ['asset_id']

    asset_id = models.CharField(max_length=settings.DEFAULT_MAX_CHAR)
    description = models.TextField(blank=True, null=True)
    accounting_status = models.CharField(
        max_length=8,
        choices=accounting.AccountingStatus,
        default=accounting.AccountingStatus.RENTED
    )

    def __str__(self):
        return self.asset_id

class Asset(AssetABC):
    #name = models.CharField(max_length=settings.DEFAULT_MAX_CHAR)
    tags = TaggableManager(blank=True)

class Inventory(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=settings.DEFAULT_MAX_CHAR)
    amount = models.FloatField()
    dimension = models.CharField(
        max_length=13,
        choices=core.Dimension.choices,
        default=core.Dimension.QUANTITY,
    )
    description = models.TextField(blank=True, null=True)

class MaterialInventory(Inventory):
    class Meta:
        verbose_name = 'Material Inventory'
        verbose_name_plural = 'Material Inventories'

    material_category = models.ForeignKey(
        MaterialHiCat,
        on_delete=models.PROTECT
    )
    history = HistoricalRecords()

class ProductInventory(Inventory):
    class Meta:
        verbose_name = 'Product Inventory'
        verbose_name_plural = 'Product Inventories'

    product_category = models.ForeignKey(ProductHiCat, on_delete=models.PROTECT)
    tags = TaggableManager(blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return self.name
