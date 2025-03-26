from django.utils import timezone
from rest_framework import serializers

from coverage.models import Coverage, Policy
from logistics.models import Shipment
from procurement.models import Party
from vessels.models import Document, Vessel


class BillOfLadingSerializer(serializers.Serializer):

    bl_number = serializers.CharField(source='number')

    class Meta:
        model = Shipment


class PartySerializer(serializers.ModelSerializer):

    class Meta:
        model = Party
        fields = ['name']


class PolicySerializer(serializers.ModelSerializer):

    insured = PartySerializer()
    provider = PartySerializer()

    class Meta:
        model = Policy
        fields = ['number', 'provider', 'insured', 'expiry']


class CoverageSerializer(serializers.ModelSerializer):

    policy = PolicySerializer()
    premium = serializers.ReadOnlyField()

    class Meta:
        model = Coverage
        fields = [
            'shipment',
            'policy',
            'debit_note',
            'date',
            'ordinary_risks_rate',
            'war_risks_rate',
            'premium'
        ]


class FormMergeSerializer(serializers.Serializer):

    deal_number = serializers.CharField(source='number')
    insured = serializers.CharField(source='coverage.policy.insured')
    address = serializers.CharField(source='coverage.policy.insured.address')
    beneficiary = serializers.CharField(source='contract.buyer')
    beneficiary_address = serializers.CharField(
        source='contract.buyer.address'
    )
    surveyor_loadport = serializers.CharField(source='surveyor_loadport.name')
    surveyor_disport = serializers.CharField(source='surveyor_disport.name')
    basis_of_valuation = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    # bl_number = BillOfLadingSerializer(many=True)
# =============================================================================
#     TODO: Implement Handle to Generate the Following Output:
#         "bl_number": [
#             {
#                 "bl_number": "Bill of Lading #\u00a0SILNVS25117500 dated 19\u00a0March\u00a02025"
#             }
#         ],
# =============================================================================
    bl_date = serializers.CharField(source='date')
    loadport = serializers.CharField(max_length=16)
    disport = serializers.CharField(max_length=16)
    policy_number = serializers.CharField(source='coverage.policy.number')
    policy_date = serializers.CharField(source='coverage.policy.inception')
    subject_matter_insured = serializers.CharField(max_length=16)
    vessel = serializers.CharField(source='vessel.name')
    imo = serializers.CharField(source='vessel.imo')
    year_built = serializers.SerializerMethodField()
    weight_metric = serializers.SerializerMethodField(read_only=True)
    sum_insured = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Shipment
        fields = [
            'deal_number',
            'insured',
            'address',
            'beneficiary',
            'beneficiary_address',
            'surveyor_loadport',
            'surveyor_disport',
            'basis_of_valuation',
            'date',
            'bl_number',
            'bl_date',
            'loadport',
            'disport',
            'policy_number',
            'policy_date',
            'subject_matter_insured',
            'vessel',
            'imo',
            'year_built',
            'weight_metric',
            'sum_insured',
        ]

    def get_basis_of_valuation(self, obj):
        return '100%'

    def get_date(self, obj):
        today = timezone.now().date()
        return min(obj.date, today)

    def get_sum_insured(self, obj):
        return f'{obj.ccy} {float(obj.sum_insured):,.2f}'

    def get_weight_metric(self, obj):
        return f'{obj.weight_metric:,.3f}'

    def get_year_built(self, obj):
        return f'{obj.vessel.built_on.year}'


class VesselSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vessel
        fields = ['name', 'imo', 'built_on']


class DocumentSerializer(serializers.ModelSerializer):

    vessel = VesselSerializer()
    provider = PartySerializer()
    is_valid = serializers.ReadOnlyField()

    class Meta:
        model = Document
        fields = '__all__'
