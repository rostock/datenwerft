from rest_framework import serializers
from .models import MetadataTemplate, MetadataField


class MetadataFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetadataField
        fields = ['id', 'name', 'description', 'field_type', 'is_required', 'options', 'order']


class MetadataTemplateSerializer(serializers.ModelSerializer):
    fields = MetadataFieldSerializer(many=True, read_only=True)
    
    class Meta:
        model = MetadataTemplate
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'is_active', 'fields']
