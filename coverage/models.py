from django.db import models

from core.constants import MAX_LENGTH_REF
from logistics.models import Shipment
from procurement.models import Party


class Coverage(models.Model):

    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
    policy = models.ForeignKey(
        'Policy',
        on_delete=models.SET_NULL,
        verbose_name='Underwriter`s Policy',
        blank=True,
        null=True
    )
    debit_note = models.CharField(
        verbose_name='Underwriter`s Debit Note',
        max_length=MAX_LENGTH_REF,
        default='#'
    )
    date = models.DateField(
        auto_now_add=True,
        verbose_name='Date Risk Processed'
    )
    ordinary_risks_rate = models.DecimalField(
        verbose_name='Standard Coverage Rate',
        decimal_places=8,
        max_digits=9,
        default=.0
    )
    war_risks_rate = models.DecimalField(
        verbose_name='War Risks Rate',
        decimal_places=8,
        max_digits=9,
        default=.0
    )

    @property
    def sum_insured(self):
        return 1.0

    @property
    def premium(self):
        return 1.0


class Policy(models.Model):

    number = models.CharField(max_length=MAX_LENGTH_REF)
    provider = models.ForeignKey(
        Party,
        on_delete=models.CASCADE,
    )
    insured = models.ForeignKey(
        Party,
        on_delete=models.CASCADE,
    )
    date = models.DateField()
    inception = models.DateTimeField()
    expiry = models.DateTimeField()
