from rest_framework import serializers
from .models import Litigation, Reference, Title


class ReferenceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reference
        fields = ( 'reference', 'reference_text')


class TitleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Title
        fields = ( 'title_text', 'priority')


class LitigationSerializer(serializers.HyperlinkedModelSerializer):
    references = ReferenceSerializer(many=True, read_only=True, source='litigation_fk_reference')
    titles = TitleSerializer(many=True, read_only=True, source='litigation_fk_title')

    class Meta:
        model = Litigation
        fields = ('release_no', 'date', 'respondents', 'content', 'people', 'organizations', 'references', 'titles')


