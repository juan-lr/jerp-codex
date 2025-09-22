import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from simple_history.models import HistoricalRecords

from organizations.models import OrgObject, HierarchicalOrgCode
from django.conf import settings


def get_currencies():
    return {i: i for i in settings.CURRENCIES}

class AccountingStatus(models.TextChoices):
    OWNED = 'owned', _('Owned')
    RENTED = 'rented', _('Rented')
    ARCHIVED = 'archived', _('Archived')

class AccountingActivityHiCat(HierarchicalOrgCode):
    class Meta:
        verbose_name = "Accounting Activity Category"
        verbose_name_plural = "Accounting Activity Categories"

class AccountingProductHiCat(HierarchicalOrgCode):
    class Meta:
        verbose_name = "Accounting Product Category"
        verbose_name_plural = "Accounting Product Categories"

class AccountingBucketHiCat(HierarchicalOrgCode):
    class Meta:
        verbose_name = "Accounting Bucket"
        verbose_name_plural = "Accounting Buckets"

class CashFlowItem(OrgObject):
    class Meta:
        verbose_name = "Cash Flow Item"
        verbose_name_plural = "Cash Flow Items"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    accounting_activity = models.ForeignKey(
        AccountingActivityHiCat,
        on_delete=models.PROTECT
    )
    accounting_bucket = models.ForeignKey(
        AccountingBucketHiCat,
        on_delete=models.PROTECT
    )
    amount = models.FloatField(blank=True, null=True)
    currency = models.CharField(
        max_length=3,
        choices=get_currencies,
        default=settings.DEFAULT_CURRENCY
    )
    history = HistoricalRecords()
