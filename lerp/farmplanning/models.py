from django.db import models
from django.db.models import PROTECT
from django.db.models import CheckConstraint
from django.db.models.expressions import RawSQL
from django.core.validators import MinValueValidator

from mptt.models import MPTTModel, TreeForeignKey

from datetime import date

from django.conf import settings
import core.models as core
import organizations.models as orgs
import accounting.models as accounting
import resources.models as resources
import equipment.models as equipment
import realestate.models as realestate


def create_bool_sum_constraint(
    field_names,
    constraint_name,
    database_backend='postgresql'
) -> CheckConstraint:
    """ Creates a constraint using RawSQL expression """
    sql_expression = (
        ' + '.join(
            [f'({field} IS NOT NULL)::int' for field in field_names]
        )
        + ' = 1'
    )

    return [CheckConstraint(
        condition=RawSQL(sql_expression, [], output_field=models.BooleanField()),
        name=constraint_name,
        violation_error_message=f"Exactly one of {', '.join(field_names)} must be non-null."
    )]

# ==============================================================================
# High-level Human-Oriented Containers
# ==============================================================================

class RanchPlan(models.Model):
    ranch = models.ForeignKey(realestate.Ranch, on_delete=PROTECT)
    name = models.CharField(
        max_length=settings.DEFAULT_MAX_CHAR,
        unique=True,
    )

    def __str__(self):
        return self.name

class CropPlan(models.Model):
    name = models.CharField(max_length=settings.DEFAULT_MAX_CHAR, unique=True)
    product = models.ForeignKey(resources.ProductHiCat, on_delete=PROTECT)
    # TODO: default to unix ref: 1970-01-01 for use with absolute Activity dates
    ref_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name

    def clone():
        # deep copy with name = name_copy
        ...

    def to_field_plan(self, field: realestate.Field, ranch_plan: RanchPlan):
        ...

class FieldPlan(models.Model):
    crop_plan = models.ForeignKey(CropPlan, on_delete=PROTECT)
    ranch_plan = models.ForeignKey(RanchPlan, on_delete=PROTECT)
    field = models.ForeignKey(realestate.Field, on_delete=PROTECT)

# ==============================================================================
# Activities
# ==============================================================================

class FieldActivityABC(models.Model):
    time_from_ref_date = models.DurationField(blank=True, null=True)
    category = models.ForeignKey(resources.ActivityHiCat, on_delete=PROTECT)

class CropPlanFieldActivity(FieldActivityABC):
    crop_plan = models.ForeignKey(
        CropPlan,
        on_delete=PROTECT,
        blank=True,
        null=True
    )

    def __str__(self):
        return f'{self.crop_plan} | {self.category}'

    def to_field_activity(self, field_plan):
        return FieldActivity.objects.create(field_plan=field_plan)

class FieldActivity(FieldActivityABC):
    field_plan = models.ForeignKey(FieldPlan, on_delete=PROTECT)
    is_actual = models.BooleanField(default=False)

# ==============================================================================
# Activity Dependencies
# ==============================================================================
# FAD = FieldActivityDependency

class FADBoolEnum(orgs.OrgDBEnum):
    class Meta:
        verbose_name = 'Field Activity Dependency Enum (Bool)'
        verbose_name_plural = 'Field Activity Dependencies Enum (Bool)'


class FADBool(models.Model):
    """
    NOTE: reference is to CropPlanFieldActivity NOT FieldActivity!
    FieldActivity are included/dropped when at CropPlan.to_field_plan
    Therefore, FADs are not (strictly) required in FieldActivity-s.
    If you really need FADs (e.g. need to re-evaluate need for an activity
    mid-season due to changing conditions), see CropPlan attached to FieldPlan.
    """

    class Meta:
        unique_together = [('field_activity', 'dependency')]
        verbose_name = 'Field Activity Dependency (Bool)'
        verbose_name_plural = 'Field Activity Dependencies (Bool)'

    # consider check for (crop_plan_)field_activity.org == dependency.org
    field_activity = models.ForeignKey(CropPlanFieldActivity, on_delete=PROTECT)
    dependency = models.ForeignKey(FADBoolEnum, on_delete=PROTECT)

"""
class FADFloatEnum(orgs.OrgDBEnum):
    comparison = choice of ==, !=, >=, etc.
    comparison_value = models.FloatField()
"""

class FADBoolValue(models.Model):
    class Meta:
        unique_together = [('field', 'dependency')]
        verbose_name = 'Field Activity Dependency Bool Value'
        verbose_name_plural = 'Field Activity Dependency Bool Values'

    # consider check for field.org == dependency.org
    field = models.ForeignKey(realestate.Field, on_delete=PROTECT)
    dependency = models.ForeignKey(FADBoolEnum, on_delete=PROTECT)
    value = models.BooleanField(blank=True, null=True)

# ==============================================================================
# ActivityResources and ___ActivityElements
# ==============================================================================

class ActivityResource(models.Model):
    class Meta:
        abstract = True

    # Must define category/instance in child
    # Get amount dim from category/model
    amount = models.FloatField(validators=[MinValueValidator(0)])

class ActivityLabor(ActivityResource):
    category = models.ForeignKey(resources.LaborHiCat, on_delete=PROTECT)

class ActivityMaterial(ActivityResource):
    category = models.ForeignKey(resources.MaterialHiCat, on_delete=PROTECT)

class ActivityTractor(ActivityResource):
    instance = models.ForeignKey(equipment.Tractor, on_delete=PROTECT)

class ActivityImplement(ActivityResource):
    instance = models.ForeignKey(equipment.Implement, on_delete=PROTECT)

class CropPlanFieldActivityElement(models.Model):
    class Meta:
        constraints = create_bool_sum_constraint(
            field_names=[
                'labor_id',
                'material_id',
                'tractor_id',
                'implement_id'
            ],
            constraint_name='exactly_one_cpfae_field'
        )

    crop_plan_field_activity = models.ForeignKey(
        CropPlanFieldActivity,
        on_delete=PROTECT
    )

    labor = models.ForeignKey(
        resources.LaborHiCat,
        on_delete=PROTECT,
        blank=True,
        null=True
    )
    material = models.ForeignKey(
        resources.MaterialHiCat,
        on_delete=PROTECT,
        blank=True,
        null=True
    )
    tractor = models.ForeignKey(
        equipment.TractorModel,
        on_delete=PROTECT,
        blank=True,
        null=True
    )
    implement = models.ForeignKey(
        equipment.ImplementHiCat,
        on_delete=PROTECT,
        blank=True,
        null=True
    )

    def element(self):
        pot_elements = [self.labor, self.material, self.tractor, self.implement]
        non_null_element = None
        for element in pot_elements:
            if element is not None:
                non_null_element = element

        return non_null_element

    def __str__(self):
        return f'{self.crop_plan_field_activity} | {self.element()}'

    def to_field_activity_element(self, ):
        field_activity_element = FieldActivityElement.objects.create()

class FieldActivityElement(models.Model):
    class Meta:
        constraints = create_bool_sum_constraint(
            field_names=[
                'labor_id',
                'material_id',
                'tractor_id',
                'implement_id'
            ],
            constraint_name='exactly_one_fae_field'
        )

    field_activity = models.ForeignKey(FieldActivity, on_delete=PROTECT)

    labor = models.ForeignKey(
        ActivityLabor,
        on_delete=PROTECT,
        blank=True,
        null=True
    )
    material = models.ForeignKey(
        ActivityMaterial,
        on_delete=PROTECT,
        blank=True,
        null=True
    )
    tractor = models.ForeignKey(
        ActivityTractor,
        on_delete=PROTECT,
        blank=True,
        null=True
    )
    implement = models.ForeignKey(
        ActivityImplement,
        on_delete=PROTECT,
        blank=True,
        null=True
    )

    def to_acc_cfi():
        raise NotImplementedError
