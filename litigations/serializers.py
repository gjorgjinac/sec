from rest_framework import serializers
from .models import Litigation, Reference, Title


class ReferenceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reference
        fields = ('litigation', 'reference', 'reference_text')


class LitigationSerializer(serializers.HyperlinkedModelSerializer):
    references = ReferenceSerializer(many=True, read_only=True)
    class Meta:
        model = Litigation
        fields = ('release_no', 'date', 'respondents', 'content', 'people', 'organizations', 'references')


class TitleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Title
        fields = ('litigation', 'title_text', 'priority')
