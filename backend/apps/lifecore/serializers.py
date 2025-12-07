from rest_framework import serializers
from .models import Observation, TimelineEvent, ConsentPolicy, DoctorShareLink, Document


class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observation
        fields = ['id', 'user', 'code', 'value', 'unit', 'taken_at', 'source', 'extra']
        read_only_fields = ['id']


class TimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimelineEvent
        fields = ['id', 'user', 'kind', 'payload', 'occurred_at']
        read_only_fields = ['id']


class ConsentPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsentPolicy
        fields = ['id', 'user', 'resource', 'purpose', 'allowed', 'scope', 'expires_at']
        read_only_fields = ['id']


class DoctorShareLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorShareLink
        fields = ['token', 'scope', 'expires_at', 'revoked']
        read_only_fields = ['token']


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'user', 'title', 'content', 'source', 'created_at']
        read_only_fields = ['id', 'created_at']
