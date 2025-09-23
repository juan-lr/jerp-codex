from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from mptt.models import MPTTModel, TreeForeignKey

from django.conf import settings
from pint import UnitRegistry

ureg = UnitRegistry(system=settings.UNIT_SYSTEM)
"""
# Unit Naming Convention
<unit>_<power-sign><power> where:
    - <unit> is an SI base unit
    - <power-sign> is `p` (positive) or `m` (minus)
    - you may leave out _p1

If using multiple base units, use `__` (double underscore) for multiplication.
"""

SI_DIMENSION_UNIT = {
    'area': 'meter_p2',
    'density': 'mass__meter_m3',
    'speed': 'meter_second_m1',
    'volume': 'meter_p3',
}

def parse_sign(char: str) -> str:
    if not isinstance(char, str):
        raise TypeError(f'Got an invalid sign: {char}. Must be "p" or "m"')
    if char not in ['p', 'm']:
        raise ValueError(f'Got an invalid sign: {char}. Must be "p" or "m"')

    return '+' if char == 'p' else '-'

def is_int(potential_int) -> bool:
    try:
        int(potential_int)
        return True
    except:
        return False

def parse_si_unit(derived_unit: str):
    py_format = ''
    units = derived_unit.split('__')
    for unit in units:
        base_unit, power = unit.split('_')
        sign, power = power[0], power[1:]
        if is_int(power):
            return f'{base_unit} ** {sign}{power}'
        else:
            ValueError(f'Got a non-integer power: {power}')

def register_si_units():
    for dimension, unit in SI_DIMENSION_UNIT:
        ureg.define(f'{unit} = {parse_si_unit(unit)}')

# ==============================================================================
# Physical Primatives
# ==============================================================================

class Dimension(models.TextChoices):
    DIMENSIONLESS = 'dimensionles', _('dimensionless')
    QUANTITY = 'quantity', _('quantity')

    AREA = 'area', _('area')
    DENSITY = 'density', _('density')
    ENERGY = 'energy', _('energy')
    FORCE = 'force', _('force')
    LENGTH = 'length', _('length')
    MASS = 'mass', _('mass')
    SPEED = 'speed', _('speed')
    TIME = 'time', _('time')
    VOLUME = 'volume', _('volume')

# NOTE: ____Unit.value must be in ureg

class TimeUnit(models.TextChoices):
    SI_UNIT = 'second', _('seconds')
    HOUR = 'hour', _('hours')
    DAY =  'day', _('days')

class LengthUnit(models.TextChoices):
    SI_UNIT = 'meter', _('meters')
    CENTIMETER = 'centimeter', _('centimeters')
    KILOMETER = 'kilometer', _('kilometers')
    INCH = 'inch', _('inches')
    FOOT = 'foot', _('feet')
    MILE = 'mile', _('miles')

class AreaUnit(models.TextChoices):
    SI_UNIT = SI_DIMENSION_UNIT['area'], _('square meters')
    HECTACRE = 'hectare', _('hectacres')
    SQUARE_FOOT = 'sq_ft', _('square feet')
    ACRE = 'acre', _('acres')

class VolumeUnit(models.TextChoices):
    SI_UNIT = SI_DIMENSION_UNIT['volume'], _('cubic meters')
    LITER = 'liter', _('liters')
    GALLON = 'gallon', _('gallons (US)')
    # IMERIAL_GALLON = 'imperial_gallon', _('gallons (british imperial)')
    # Above likely only op for mistakes right now

class SpeedUnit(models.TextChoices):
    SI_UNIT = SI_DIMENSION_UNIT['speed'], _('meters per second')

class MassUnit(models.TextChoices):
    SI_UNIT = 'kilogram', _('kilograms')
    POUND = 'pound', _('pound')

class ForceUnit(models.TextChoices):
    SI_UNIT = 'newton', _('newtons')
    POUND_FORCE = 'pound_force', _('pounds of force')
    KILOGRAM_FORCE = 'kilogram__gravity', _('kilograms of force')

class EnergyUnit(models.TextChoices):
    SI_UNIT = 'joule', _('joules')
    FOOT_POUND = 'foot_pound', 'foot-pound'

class PowerUnit(models.TextChoices):
    SI_UNIT = 'watt', _('watt')
    HORSEPOWER = 'horsepower', _('horsepower')

# ==============================================================================
# Database Primatives
# ==============================================================================

class DBEnum(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(
        max_length=settings.DEFAULT_MAX_CHAR,
        primary_key=True
    )

    def __str__(self):
        return self.name

class HierarchicalEnumWithDesc(MPTTModel):
    class Meta:
        abstract = True
        unique_together=[('organization', 'name')]

    name = models.CharField(max_length=settings.DEFAULT_MAX_CHAR)
    description = models.TextField(blank=True, null=True)
    parent = TreeForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='children'
    )

    def __str__(self):
        return self.name
