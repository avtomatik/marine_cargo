# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 12:59:19 2025

@author: Aleksandr.Mikhailov
"""

import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from logistics.models import Shipment


class Command(BaseCommand):

    PATH_DATA = 'data'

    FILE_NAME = 'logistics_shipment.csv'

    FIELD_NAMES = [
        'number',
        'date',
        'disport_eta',
        'volume_bbl',
        'weight_metric',
        'ccy',
        'unit',
        'subject_matter_insured',
        'contract_id',
        'disport_id',
        'loadport_id',
        'operator_id',
        'surveyor_disport_id',
        'surveyor_loadport_id',
        'sum_insured',
        'vessel_id'
    ]

    PATH = settings.BASE_DIR.joinpath(PATH_DATA)

    help = 'Populates DB with Shipments Data'

    def handle(self, *args, **options):

        with self.PATH.joinpath(self.FILE_NAME).open(encoding='utf8') as file:
            reader = csv.DictReader(file, fieldnames=self.FIELD_NAMES)
            next(reader)
            Shipment.objects.bulk_create(Shipment(**_) for _ in reader)

        self.stdout.write(
            self.style.SUCCESS('Successfully Populated DB with Shipments Data')
        )
